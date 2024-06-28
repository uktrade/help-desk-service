import mimetypes
import os
import re
from abc import ABCMeta, abstractmethod
from datetime import datetime
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from email.utils import parseaddr

import requests
from markdown import markdown
from zenpy import Zenpy
from zenpy.lib.api_objects import Comment, Ticket, User


class ParsedEmail:
    # RFC 5322 section 3.4 specifies that the display name  /PS-IGNORE
    # in a `mailbox` is optional, but Zendesk
    # needs one for the `requester` value.
    FALLBACK_DISPLAY_NAME = "unknown"

    message: EmailMessage
    ticket_id_matcher: str = r"\[IN-0*(\d+)]"

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
        upload_tokens = self.upload_attachments(message.attachments)
        if ticket_id := message.reply_to_ticket_id:
            response = self.update_ticket(message, upload_tokens, ticket_id)
        else:
            response = self.create_ticket(message, upload_tokens=upload_tokens)
        return response

    def upload_attachments(self, attachments):
        upload_tokens = []
        for attachment in attachments:
            payload = attachment["payload"]
            filename = attachment["filename"]
            content_type = attachment["content_type"]
            upload = self.upload_attachment(
                payload=payload, target_name=filename, content_type=content_type
            )
            upload_tokens.append(upload.token)
        return upload_tokens

    @abstractmethod
    def upload_attachment(self, payload, target_name, content_type):
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
        print(f"Init APIClient with email {zendesk_email} and token {zendesk_token}")
        self.client = Zenpy(subdomain="staging-uktrade", email=zendesk_email, token=zendesk_token)

    def upload_attachment(self, payload, target_name, content_type="application/octet-stream"):
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
        print(f"Posting with subject {subject}")

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

    def __init__(self, halo_subdomain, halo_client_id, halo_client_secret) -> None:
        super().__init__()
        self.halo_token = self.__authenticate(
            halo_subdomain=halo_subdomain,
            halo_client_id=halo_client_id,
            halo_client_secret=halo_client_secret,
        )

    def __authenticate(self, halo_subdomain, halo_client_id, halo_client_secret):
        data = {
            "grant_type": "client_credentials",
            "client_id": halo_client_id,
            "client_secret": halo_client_secret,
            "scope": "all",
        }
        response = requests.post(
            f"https://{halo_subdomain}.haloitsm.com/auth/token",  # /PS-IGNORE
            data=data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
        )
        if response.status_code != 200:
            message = f"{response.status_code} response from Halo auth endpoint"  # /PS-IGNORE
            raise HaloClientNotFoundException(message)

        response_data = response.json()
        return response_data["access_token"]

    def upload_attachment(self, payload, target_name, content_type):
        pass

    def create_ticket(self, message, upload_tokens):
        pass

    def update_ticket(self, message, upload_tokens, ticket_id):
        pass
