import json
from unittest import mock
from unittest.mock import MagicMock

from email_router.ses_email_receiving.email_utils import APIClient


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
                "comment": {
                    "body": parsed_email.payload,
                    "attachments": mocked_upload_tokens,
                },
                "recipient": "test@example.example",  # /PS-IGNORE
            }
        }
        mock_requests.post.assert_called_once_with(
            "http://localhost:8000/api/v2/tickets.json",  # /PS-IGNORE
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
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
            headers={
                "Content-Type": attachment["content_type"],
                "Content-Disposition": "attachment;filename=padana-2.jpg",
                "Accept": "application/json",
            },
            auth=expected_auth,
            data=attachment["payload"],
        )
