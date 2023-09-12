import base64
import json
import mimetypes
from datetime import datetime
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser

import requests


class ParsedEmail:
    message: EmailMessage

    def __init__(self, raw_bytes):
        # Parse the email from raw bytes
        self.message = BytesParser(policy=policy.default).parse(raw_bytes)

    @property
    def sender(self):
        # Get the From header and decode it if necessary
        return self.message.get("From")

    @property
    def subject(self):
        return self.message.get("Subject")

    @property
    def body(self) -> EmailMessage:
        return self.message.get_body()

    @property
    def payload(self):
        return self.body.get_content()

    @property
    def attachments(self):
        attachment: EmailMessage
        for attachment in self.message.iter_attachments():
            content_type = attachment.get_content_type()
            extension = mimetypes.guess_extension(content_type, strict=False) or ".dat"
            timestamp = datetime.utcnow().isoformat()
            filename = attachment.get_filename(failobj=f"attachment-{timestamp}{extension}")
            yield {
                "content_type": content_type,
                "filename": filename,
                "payload": attachment.get_content(),
            }


class APIClient:
    def __init__(self, zendesk_email, zendesk_token) -> None:
        super().__init__()
        self.auth = (f"{zendesk_email}/token", zendesk_token)
        creds = f"{zendesk_email}/token:{zendesk_token}"
        encoded_creds = base64.b64encode(creds.encode("ascii"))  # /PS-IGNORE
        self.auth_header = f"Basic {encoded_creds.decode('ascii')}"

    def create_ticket_from_message(self, message: ParsedEmail):
        upload_tokens = self.upload_attachments(message.attachments)
        zendesk_response = self.create_ticket(message, uploads=upload_tokens)
        return zendesk_response

    def upload_attachments(self, attachments):
        upload_url = "http://localhost:8000/api/v2/uploads.json"  # /PS-IGNORE
        upload_tokens = []
        for attachment in attachments:
            params = {"filename": attachment["filename"]}
            headers = {"Content-Type": attachment["content_type"]}
            upload_response = requests.post(
                upload_url,
                params=params,
                headers=headers,
                auth=self.auth,
                data=attachment["payload"],
            )
            upload_response_json = upload_response.json()
            upload_token = upload_response_json["upload"]["token"]
            upload_tokens.append(upload_token)
        return upload_tokens

    def create_ticket(self, message, uploads=None):
        ticket_creation_url = "http://localhost:8000/api/v2/tickets.json"  # /PS-IGNORE
        content_type = "application/json"
        ticket_data = {
            "ticket": {
                "subject": message.subject,
                "requester": message.sender,
                "comment": {
                    "body": message.payload,
                },
                "group_id": 10372467296924,
            }
        }
        if uploads:
            ticket_data["ticket"]["comment"]["uploads"] = uploads
        zendesk_response = requests.post(
            ticket_creation_url,
            headers={
                "Content-Type": content_type,
            },
            auth=self.auth,
            data=json.dumps(ticket_data),
        )
        return zendesk_response
