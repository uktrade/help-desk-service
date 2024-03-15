import base64
import mimetypes
from datetime import datetime
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from email.utils import parseaddr

from markdown import markdown
from zenpy import Zenpy
from zenpy.lib.api_objects import Comment, CustomField, Ticket, User


class ParsedEmail:
    # RFC 5322 section 3.4 specifies that the display name  /PS-IGNORE
    # in a `mailbox` is optional, but Zendesk
    # needs one for the `requester` value.
    FALLBACK_DISPLAY_NAME = "unknown"

    message: EmailMessage

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


class APIClient:
    def __init__(
        self, zendesk_email, zendesk_token, api_url="http://localhost:8000/api/v2/"  # /PS-IGNORE
    ) -> None:
        super().__init__()
        self.api_url = api_url
        self.auth = (f"{zendesk_email}/token", zendesk_token)
        creds = f"{zendesk_email}/token:{zendesk_token}"
        encoded_creds = base64.b64encode(creds.encode("ascii"))  # /PS-IGNORE
        self.auth_header = f"Basic {encoded_creds.decode('ascii')}"
        self.client = Zenpy(subdomain="staging-uktrade", email=zendesk_email, token=zendesk_token)

    def create_ticket_from_message(self, message: ParsedEmail):
        upload_tokens = self.upload_attachments(message.attachments)
        zendesk_response = self.create_ticket(message, uploads=upload_tokens)
        return zendesk_response

    def upload_attachments(self, attachments):
        upload_tokens = []
        for attachment in attachments:
            payload = attachment["payload"]
            filename = attachment["filename"]
            content_type = attachment["content_type"]
            upload = self.client.attachments.upload(
                payload, target_name=filename, content_type=content_type
            )
            upload_tokens.append(upload.token)
            return upload_tokens

    def create_ticket(self, message: ParsedEmail, upload_tokens=None):
        timestamp = datetime.utcnow().isoformat()
        subject = f"{message.subject} (Posted by AWS Lambda at {timestamp})"
        description = message.payload
        recipient = parseaddr(message.recipient)[1]

        zenpy_user = User(
            email=f"test-{datetime.utcnow().microsecond}-{message.sender_email}",
            name=f"test-{datetime.utcnow().microsecond} {message.sender_name}",
        )
        zenpy_ticket = Ticket(
            subject=subject,
            comment=Comment(
                html_body=description,
                uploads=upload_tokens,
            ),
            requester=zenpy_user,
            custom_fields=[CustomField(id=31281329, value="datahub")],
            recipient=recipient,
        )

        ticket_audit = self.client.tickets.create(zenpy_ticket)
        return ticket_audit
