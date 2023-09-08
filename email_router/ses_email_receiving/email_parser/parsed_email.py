from email import policy
from email.message import EmailMessage
from email.parser import BytesParser


class ParsedEmail:
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
        return self.body.get_payload(decode=True)

    @property
    def attachments(self):
        return list(self.message.iter_attachments())
