from datetime import datetime
from email.message import EmailMessage
from unittest import mock
from unittest.mock import MagicMock

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

        assert "Posted at {{ timestamp }}: {{ message_text}}" in payload  # /PS-IGNORE

    def test_attachments(self, parsed_email):
        attachments = list(parsed_email.attachments)
        attachment = attachments[0]

        assert attachment["content_type"] == "image/jpeg"
        assert attachment["filename"] == "padana-2.jpg"
        assert "payload" in attachment
        assert isinstance(attachment["payload"], bytes)

    @mock.patch("mimetypes.guess_extension")  # /PS-IGNORE
    @mock.patch("email_router.ses_email_receiving.email_utils.datetime")
    def test_attachment_without_filename_gets_default_filename(
        self, mock_datetime: MagicMock, mock_guess_extension: MagicMock, parsed_email
    ):
        mock_guess_extension.return_value = None
        mocked_datetime = datetime(year=2001, month=9, day=11, hour=8, minute=43)
        mock_datetime.utcnow.return_value = mocked_datetime
        with mock.patch("email.message._unquotevalue") as mock_unquote_value:
            with mock.patch("email.message.object") as mock_object_constructor:
                """
                These mocks are necessary to prevent get_filename finding
                the real filename of the attachment, thus making it use
                the fallback value provided to it in the failobj argument.
                """
                mock_missing_value = "missing_value"
                mock_object_constructor.return_value = mock_missing_value
                mock_unquote_value.return_value = mock_missing_value

                attachment = list(parsed_email.attachments)[0]
        expected_datetime = mocked_datetime.isoformat()

        assert attachment["filename"] == f"attachment-{expected_datetime}.dat"


class TestNameAndEmail:
    def test_get_sender_name_without_email_address(self, parsed_outlook_email):
        expected_sender_name = "Some BODY (DBT)"

        sender_name = parsed_outlook_email.sender_name

        assert sender_name == expected_sender_name

    def test_get_sender_email_address_without_name(self, parsed_outlook_email):
        expected_sender_email = "some.body@example.com"  # /PS-IGNORE

        sender_email = parsed_outlook_email.sender_email

        assert sender_email == expected_sender_email

    def test_sender_name_fallback_to_email_username_part(self, simple_mailbox_from_email):
        expected_sender_name = ParsedEmail.FALLBACK_DISPLAY_NAME

        sender_name = simple_mailbox_from_email.sender_name

        assert sender_name == expected_sender_name
