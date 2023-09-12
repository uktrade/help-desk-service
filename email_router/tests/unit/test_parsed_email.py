from email.message import EmailMessage

from email_router.ses_email_receiving.email_utils import ParsedEmail


class TestParsedEmail:
    def test_from_address(self, parsed_email: ParsedEmail):
        from_address = parsed_email.sender

        expected_username = "User, Test"
        expected_email_address = "example@digital.trade.gov.uk"  # /PS-IGNORE
        assert f'"{expected_username}" <{expected_email_address}>' in from_address

    def test_subject(self, parsed_email: ParsedEmail):
        subject = parsed_email.subject

        expected_subject = "Two JPG attachments"
        assert subject == expected_subject

    def test_html_body(self, parsed_email: ParsedEmail):
        body: EmailMessage = parsed_email.body

        assert body.get_content_type() == "text/html"

    def test_decoded_payload(self, parsed_email):
        payload = parsed_email.payload

        assert b"&quot;Actually it&#39;s JPEG&quot; yeah, yeah, whatever." in payload  # /PS-IGNORE

    def test_attachments(self, parsed_email):
        attachments = parsed_email.attachments

        assert len(attachments) == 2
