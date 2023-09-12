import json
from datetime import datetime
from email.message import EmailMessage
from unittest import mock
from unittest.mock import MagicMock

from email_router.ses_email_receiving.email_utils import APIClient, ParsedEmail


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
    def test_attachment_gets_default_filename(
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


class TestAPIClient:
    @mock.patch("email_router.ses_email_receiving.email_utils.requests")
    @mock.patch("email_router.ses_email_receiving.email_utils.APIClient.upload_attachments")
    def test_create_ticket_from_message(
        self, mock_upload_attachments: MagicMock, mock_requests: MagicMock, parsed_email
    ):
        mocked_upload_tokens = ["123", "ABC"]
        mock_upload_attachments.return_value = mocked_upload_tokens

        client = APIClient(zendesk_email="test@example.com", zendesk_token="aaa")  # /PS-IGNORE
        client.create_ticket_from_message(parsed_email)

        expected_ticket_data = {
            "ticket": {
                "subject": parsed_email.subject,
                "requester": parsed_email.sender,
                "comment": {
                    "body": parsed_email.payload,
                    "uploads": mocked_upload_tokens,
                },
                "group_id": 10372467296924,
            }
        }
        mock_requests.post.assert_called_once_with(
            "http://localhost:8000/api/v2/tickets.json",  # /PS-IGNORE
            headers={
                "Content_Type": "application/json",
            },
            auth=client.auth,
            data=json.dumps(expected_ticket_data),
        )

    @mock.patch("email_router.ses_email_receiving.email_utils.requests")
    def test_upload_attachments(
        self, mock_requests: MagicMock, parsed_email, zendesk_upload_response
    ):
        zendesk_email = "test@example.com"  # /PS-IGNORE
        zendesk_token = "aaa"
        client = APIClient(zendesk_email=zendesk_email, zendesk_token=zendesk_token)
        mock_requests.post.return_value = zendesk_upload_response

        attachment = list(parsed_email.attachments)[0]
        upload_tokens = client.upload_attachments([attachment])

        assert upload_tokens == ["1234"]
        expected_auth = (f"{zendesk_email}/token", zendesk_token)
        mock_requests.post.assert_called_once_with(
            "http://localhost:8000/api/v2/uploads.json",  # /PS-IGNORE
            params={"filename": attachment["filename"]},
            headers={"Content-Type": attachment["content_type"]},
            auth=expected_auth,
            data=attachment["payload"],
        )
