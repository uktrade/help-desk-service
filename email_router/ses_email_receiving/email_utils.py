import base64
import json
import mimetypes
import os
import re
from abc import ABCMeta, abstractmethod
from datetime import datetime
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from email.utils import parseaddr
from http import HTTPStatus

import requests
from aws_lambda_powertools.logging.logger import Logger
from markdown import markdown
from requests import HTTPError, Response
from zenpy import Zenpy
from zenpy.lib.api_objects import Comment, Ticket, User

logger: Logger = Logger()
logger.setLevel("DEBUG" if os.environ.get("DEBUG", False) else "INFO")


class ParsedEmail:
    # RFC 5322 section 3.4 specifies that the display name  /PS-IGNORE
    # in a `mailbox` is optional, but Zendesk
    # needs one for the `requester` value.
    FALLBACK_DISPLAY_NAME = "unknown"

    message: EmailMessage
    ticket_id_matcher: str = r"\[[[A-Z]{2}-0*(\d+)]"

    def __init__(self, raw_bytes):
        # Parse the email from raw bytes
        self.message = BytesParser(policy=policy.default).parse(raw_bytes)

    @property
    def sender(self):
        # Get the From header
        return self.message.get("From")

    @property
    def mailbox_parts(self):
        return parseaddr(self.sender)

    @property
    def sender_name(self):
        # Get the user's name from the From header
        if self.mailbox_parts[0]:
            return self.mailbox_parts[0]
        return self.FALLBACK_DISPLAY_NAME

    @property
    def sender_email(self):
        # Get the user's email address from the From header
        return self.mailbox_parts[1]

    @property
    def subject(self):
        return self.message.get("Subject")

    @property
    def body(self) -> EmailMessage:
        return self.message.get_body(preferencelist=("html", "plain"))

    @property
    def payload(self):
        payload = self.body.get_content()
        if self.body.get_content_type() == "text/plain":
            payload = markdown(payload)
        return payload

    @property
    def attachments(self):
        attachment: EmailMessage
        for attachment in self.message.iter_attachments():
            content_type = attachment.get_content_type()
            extension = mimetypes.guess_extension(content_type, strict=False) or ".dat"
            timestamp = datetime.utcnow().isoformat()
            filename = attachment.get_filename(failobj=f"attachment-{timestamp}{extension}")
            content_disposition = attachment.get_content_disposition()
            if content_disposition is None:
                # DRF insists on this for parsing a file upload…
                content_disposition = "attachment"
            yield {
                "content_type": content_type,
                "content_disposition": content_disposition,
                "filename": filename,
                "payload": attachment.get_content(),
            }

    @property
    def recipient(self):
        """
        The email address to which the ticket was sent
        TODO: consider whether, if there are multiple recipients
            or CC and BCC recipients,  /PS-IGNORE
            we should actively search for one at our custom domain
            Also, we could supply a default, maybe?
        """
        return self.message.get("To")

    @property
    def reply_to_ticket_id(self):
        if search_result := re.search(self.ticket_id_matcher, self.subject):
            return search_result.group(1)
        return None


class BaseAPIClient(metaclass=ABCMeta):
    def create_or_update_ticket_from_message(self, message: ParsedEmail):
        ticket_id = message.reply_to_ticket_id
        upload_tokens = self.upload_attachments(message, ticket_id=ticket_id)
        if ticket_id:
            logger.info("Updating ticket", extra={"ticket_id": ticket_id})
            response = self.update_ticket(message, upload_tokens, ticket_id)
        else:
            logger.info(
                f"Creating ticket {message.subject} ",
                extra={
                    "subject": message.subject,
                    "from": message.sender_email,
                    "to": message.recipient,
                },
            )
            response = self.create_ticket(message, upload_tokens=upload_tokens)
        return response

    def upload_attachments(self, message: ParsedEmail, ticket_id=None):
        from_address = message.sender_email
        upload_tokens = []
        for attachment in message.attachments:
            payload = attachment["payload"]
            filename = attachment["filename"]
            content_type = attachment["content_type"]
            upload = self.upload_attachment(
                payload=payload,
                target_name=filename,
                content_type=content_type,
                ticket_id=ticket_id,
                from_address=from_address,
            )
            upload_tokens.append(upload.token)
        return upload_tokens

    @abstractmethod
    def upload_attachment(self, payload, target_name, content_type, ticket_id=None, **kwargs):
        pass

    @abstractmethod
    def create_ticket(self, message, upload_tokens):
        pass

    @abstractmethod
    def update_ticket(self, message, upload_tokens, ticket_id):
        pass


class MicroserviceAPIClient(BaseAPIClient):
    def __init__(self, zendesk_email, zendesk_token) -> None:
        super().__init__()
        # Zenpy requires a subdomain, but this will be overridden by ZENPY_FORCE_NETLOC  /PS-IGNORE
        logger.debug(
            f"Init MicroserviceAPIClient with email {zendesk_email} and token {zendesk_token}"
        )
        self.client = Zenpy(subdomain="staging-uktrade", email=zendesk_email, token=zendesk_token)

    def upload_attachment(
        self,
        payload,
        target_name,
        content_type="application/octet-stream",
        ticket_id=None,
        **kwargs,
    ):
        logger.info(
            "Uploading attachment",
            extra={
                "attachment_filename": target_name,
                "content_type": content_type,
            },
        )
        upload = self.client.attachments.upload(
            payload, target_name=target_name, content_type=content_type
        )
        return upload

    def create_ticket(self, message: ParsedEmail, upload_tokens=None):
        subject = message.subject
        description = message.payload
        recipient = parseaddr(message.recipient)[1]

        debug_netloc = os.environ.get("ZENPY_FORCE_NETLOC", "netloc not found")
        subject = f"{subject} via {debug_netloc}"
        logger.info("Creating ticket", extra={"subject": subject})

        zenpy_user = User(
            email=message.sender_email,
            name=message.sender_name,
        )
        zenpy_comment = Comment(
            html_body=description,
            uploads=upload_tokens,
            public=True,
        )
        zenpy_ticket = Ticket(
            subject=subject,
            comment=zenpy_comment,
            requester=zenpy_user,
            recipient=recipient,
        )

        ticket_audit = self.client.tickets.create(zenpy_ticket)
        return ticket_audit

    def update_ticket(self, message: ParsedEmail, upload_tokens=None, ticket_id=None):
        logger.info("Updating ticket", extra={"ticket_id": ticket_id})
        description = message.payload
        recipient = parseaddr(message.recipient)[1]

        zenpy_user = User(
            email=message.sender_email,
            name=message.sender_name,
        )
        zenpy_comment = Comment(
            html_body=description,
            uploads=upload_tokens,
            public=True,
        )
        zenpy_ticket = Ticket(
            id=ticket_id,
            comment=zenpy_comment,
            requester=zenpy_user,
            recipient=recipient,
        )

        ticket_audit = self.client.tickets.update(zenpy_ticket)
        return ticket_audit


class HaloClientNotFoundException(Exception):
    pass


class HaloAPIClient(BaseAPIClient):
    halo_token = None
    _halo_user: [dict, None] = None

    def get_halo_user(self, search_term):
        if self._halo_user is None:
            self._halo_user = {}
            path = "Users"
            params = {"search": search_term}
            logger.debug(f"Making Halo GET: {path}, params={params}")
            response = requests.get(
                f"https://{self.halo_subdomain}.haloitsm.com/api/{path}",
                params=params,
                headers={
                    "Authorization": f"Bearer {self.halo_token}",
                },
            )
            if response.status_code == HTTPStatus.OK:
                logger.debug(f"Completed Halo GET: {response.url}")
                search_results = response.json()
                record_count = search_results["record_count"]
                logger.info(f"Halo user search result count: {record_count}")
                if record_count > 0:
                    self._halo_user = search_results["users"][0]
                    logger.debug(
                        f"Found Halo user {self._halo_user['id']} "  # /PS-IGNORE
                        f"named {self._halo_user['name']}"
                    )
            else:
                logger.warning(f"Get Halo User error: Response status {response.status_code}")
        return self._halo_user

    def __init__(self, halo_subdomain, halo_client_id, halo_client_secret) -> None:
        super().__init__()
        logger.debug(
            "Init HaloAPIClient",
            extra={
                "halo_subdomain": halo_subdomain,
                "halo_client_id": halo_client_id,
                "halo_client_secret": halo_client_secret,
            },
        )
        self.halo_subdomain = halo_subdomain
        self.halo_token = self.__authenticate(
            halo_client_id=halo_client_id,
            halo_client_secret=halo_client_secret,
        )
        self._halo_user = None

    def __authenticate(self, halo_client_id, halo_client_secret):
        data = {
            "grant_type": "client_credentials",
            "client_id": halo_client_id,
            "client_secret": halo_client_secret,
            "scope": "all",
        }
        response = requests.post(
            f"https://{self.halo_subdomain}.haloitsm.com/auth/token",  # /PS-IGNORE
            data=data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
        )
        if response.status_code != 200:
            error_message = f"{response.status_code} response from Halo auth endpoint"  # /PS-IGNORE
            logger.error(
                "Halo authentication error",
                extra={
                    "status_code": response.status_code,
                },
            )
            raise HaloClientNotFoundException(error_message)

        response_data = response.json()
        return response_data["access_token"]

    class Upload:

        def __init__(self, token=None):
            super().__init__()
            if token is None:
                logger.error("No token for Upload")
                raise ValueError("Upload must have a token")
            self.token = token

    def upload_attachment(
        self, payload, target_name, content_type, ticket_id=None, from_address=None
    ):
        logger.info(
            "Uploading attachment",
            extra={
                "attachment_filename": target_name,
                "content_type": content_type,
                "ticket_id": ticket_id,
            },
        )
        file_content_base64 = base64.b64encode(payload).decode("ascii")  # /PS-IGNORE
        base64_payload = f"data:{content_type};base64,{file_content_base64}"  # noqa: E231,E702
        halo_attachment_payload = [
            {
                "filename": target_name,
                "isimage": content_type.startswith("image"),
                "data_base64": base64_payload,  # /PS-IGNORE
            }
        ]
        if ticket_id is not None:
            halo_attachment_payload[0]["ticket_id"] = ticket_id
        response: Response = requests.post(
            f"https://{self.halo_subdomain}.haloitsm.com/api/Attachment",
            data=json.dumps(halo_attachment_payload),
            headers={
                "Authorization": f"Bearer {self.halo_token}",
                "Content-Type": "application/json",
            },
        )

        if response.status_code != HTTPStatus.CREATED:
            error_message = f"{response.status_code} response for attachment upload"
            logger.error(error_message)
            raise HTTPError(error_message)
        response_content = response.json()
        return HaloAPIClient.Upload(token=response_content["id"])

    def create_ticket(self, message, upload_tokens):
        logger.info("Creating ticket", extra={"subject": message.subject})
        request_data = self.halo_ticket_creation_data_from_message(
            message, upload_tokens=upload_tokens
        )
        response = self.post_halo_ticket(request_data)
        if response.status_code != HTTPStatus.CREATED:
            error_message = f"{response.status_code} response for create ticket"
            logger.error(error_message)
            raise HTTPError(error_message)
        return response.json()

    def post_halo_ticket(self, request_data):
        response = requests.post(
            f"https://{self.halo_subdomain}.haloitsm.com/api/Tickets",  # /PS-IGNORE
            data=json.dumps(request_data),
            headers={
                "Authorization": f"Bearer {self.halo_token}",
                "Content-Type": "application/json",
            },
        )
        if response.status_code != HTTPStatus.CREATED:
            error_message = f"{response.status_code} response for post ticket"
            logger.error(error_message)
            raise HTTPError(error_message)
        return response

    def update_ticket(self, message, upload_tokens, ticket_id):
        logger.info(
            "Updating ticket",
            extra={
                "ticket_id": ticket_id,
                "upload_tokens": upload_tokens,
            },
        )
        request_data = self.halo_ticket_action_data_from_message(message, ticket_id=ticket_id)
        logger.info(
            "Update prepared",
            extra={
                "ticket_id": ticket_id,
                "request_data": request_data,
            },
        )
        response = self.post_halo_ticket_action(request_data)
        if response.status_code != HTTPStatus.CREATED:
            error_message = f"{response.status_code} response for update ticket"
            logger.error(error_message)
            raise HTTPError(error_message)
        response_data = response.json()
        logger.info(
            "Update response",
            extra={
                "ticket_id": ticket_id,
                "response_data": response_data,
            },
        )
        return response_data

    def post_halo_ticket_action(self, request_data):
        if "ticket_id" not in request_data[0]:
            message = "Halo Action requires ticket_id"
            logger.error(
                message,
                extra={
                    "request_data": request_data,
                },
            )
            raise ValueError(message)
        response = requests.post(
            f"https://{self.halo_subdomain}.haloitsm.com/api/Actions",  # /PS-IGNORE
            data=json.dumps(request_data),
            headers={
                "Authorization": f"Bearer {self.halo_token}",
                "Content-Type": "application/json",
            },
        )
        if response.status_code != HTTPStatus.CREATED:
            error_message = f"{response.status_code} response for post ticket"
            logger.error(error_message)
            raise HTTPError(error_message)
        return response

    def halo_ticket_creation_data_from_message(
        self, message: ParsedEmail, upload_tokens=None, ticket_id=None
    ):
        request_data = {
            "summary": message.subject,
            "details_html": message.payload,
            "users_name": message.sender_name,
            "reportedby": message.sender_email,
            "user_email": message.sender_email,
            "outcome": "First User Email",
            "tickettype_id": 36,
            "dont_do_rules": False,
            "customfields": [{"name": "CFEmailToAddress", "value": message.recipient}],
        }
        halo_user = self.get_halo_user(search_term=message.sender_email)
        if halo_user:
            # add the relevant user details to the ticket
            request_data["users_name"] = halo_user["name"]
            request_data["reportedby"] = halo_user["emailaddress"]
            request_data["user_email"] = halo_user["emailaddress"]
            request_data["user_id"] = halo_user["id"]
            request_data["user"] = halo_user
        if upload_tokens:
            attachments = [{"id": upload_token} for upload_token in upload_tokens]
            request_data["attachments"] = attachments
        if ticket_id is not None:
            request_data["id"] = ticket_id
        logger.debug(
            "Ticket data from message",
            extra={
                "request_data": request_data,
            },
        )
        return [
            request_data,
        ]

    def halo_ticket_action_data_from_message(self, message: ParsedEmail, ticket_id=None):
        request_data = {
            "ticket_id": ticket_id,
            "note_html": message.payload,
            "hiddenfromuser": False,
            "outcome": "Email Update",
            "emailfrom": message.sender_email,
            "who": message.sender_name,
            "customfields": [
                {
                    "name": "CFEmailToAddress",
                    "value": message.recipient,
                }
            ],
        }
        halo_user = self.get_halo_user(search_term=message.sender_email)
        if halo_user:
            # add the relevant user details to the ticket
            request_data["who"] = halo_user["name"]
            request_data["emailfrom"] = halo_user["emailaddress"]
            request_data["user_id"] = halo_user["id"]
        logger.debug(
            "Action data from message",
            extra={
                "request_data": request_data,
            },
        )
        return [request_data]
