import json
from email.utils import parseaddr
from http import HTTPStatus
from unittest import mock, skip
from unittest.mock import MagicMock, call

from email_router.ses_email_receiving.email_utils import (
    HaloAPIClient,
    MicroserviceAPIClient,
)
from requests import Response
from zenpy.lib.api_objects import Upload


@mock.patch("email_router.ses_email_receiving.email_utils.requests.post")
class TestAPIClient:
    @property
    def auth_response(self):
        response = Response()
        response.status_code = HTTPStatus.OK
        response._content = bytes(
            json.dumps(
                {
                    "resource": "",
                    "token_type": "Bearer",  # /PS-IGNORE
                    "access_token": "ABC123",
                    "expires_in": 3600,
                }
            ),
            "utf-8",
        )
        return response

    @mock.patch(
        "email_router.ses_email_receiving.email_utils.HaloAPIClient._HaloAPIClient__authenticate"
    )
    def test_api_client_authenticates(self, mock_authenticate: MagicMock, _mock_post: MagicMock):
        halo_subdomain = "foo"
        halo_client_id = "abcdef"  # /PS-IGNORE
        halo_client_secret = "123456"
        expected_kwargs = {
            "halo_subdomain": halo_subdomain,
            "halo_client_id": halo_client_id,
            "halo_client_secret": halo_client_secret,
        }

        HaloAPIClient(
            halo_subdomain=halo_subdomain,
            halo_client_id=halo_client_id,
            halo_client_secret=halo_client_secret,
        )

        mock_authenticate.assert_called_once_with(**expected_kwargs)

    def test_api_client_requests_halo_token(self, mock_post: MagicMock):
        halo_subdomain = "foo"
        halo_client_id = "abcdef"  # /PS-IGNORE
        halo_client_secret = "123456"
        expected_url = f"https://{halo_subdomain}.haloitsm.com/auth/token"  # /PS-IGNORE
        expected_headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }
        expected_kwargs = {
            "data": {
                "grant_type": "client_credentials",
                "client_id": halo_client_id,
                "client_secret": halo_client_secret,
                "scope": "all",
            },
            "headers": expected_headers,
        }
        mock_post.return_value = self.auth_response

        HaloAPIClient(
            halo_subdomain=halo_subdomain,
            halo_client_id=halo_client_id,
            halo_client_secret=halo_client_secret,
        )

        mock_post.assert_called_once_with(expected_url, **expected_kwargs)

    @skip("TODO")
    @mock.patch("email_router.ses_email_receiving.email_utils.Zenpy")
    @mock.patch("email_router.ses_email_receiving.email_utils.User")
    @mock.patch("email_router.ses_email_receiving.email_utils.Ticket")
    def test_create_ticket_creates_zenpy_user(
        self,
        _mock_ticket,
        mock_user: MagicMock,
        mock_zenpy: MagicMock,
        parsed_email_sans_attachments,
    ):
        mock_client = MagicMock()
        mock_zenpy.return_value = mock_client
        zendesk_email = "test@example.com"  # /PS-IGNORE
        zendesk_token = "test123"
        api_client = MicroserviceAPIClient(zendesk_email, zendesk_token)
        expected_user_email = parsed_email_sans_attachments.sender_email
        expected_user_name = parsed_email_sans_attachments.sender_name
        expected_user_kwargs = {"email": expected_user_email, "name": expected_user_name}

        api_client.create_ticket(parsed_email_sans_attachments)

        mock_user.assert_called_once_with(**expected_user_kwargs)

    @skip("TODO")
    @mock.patch("email_router.ses_email_receiving.email_utils.Zenpy")
    @mock.patch("email_router.ses_email_receiving.email_utils.Comment")
    @mock.patch("email_router.ses_email_receiving.email_utils.User")
    @mock.patch("email_router.ses_email_receiving.email_utils.Ticket")
    def test_create_ticket_creates_zenpy_comment(
        self,
        _mock_ticket: MagicMock,
        mock_user: MagicMock,
        mock_comment: MagicMock,
        mock_zenpy: MagicMock,
        parsed_email_sans_attachments,
    ):
        mock_zenpy.return_value = MagicMock()
        mock_comment.return_value = MagicMock()
        mock_user.return_value = MagicMock()
        zendesk_email = "test@example.com"  # /PS-IGNORE
        zendesk_token = "test123"
        api_client = MicroserviceAPIClient(zendesk_email, zendesk_token)
        expected_comment_kwargs = {
            "html_body": parsed_email_sans_attachments.payload,
            "uploads": None,
            "public": True,
        }

        api_client.create_ticket(parsed_email_sans_attachments)

        mock_comment.assert_called_once_with(**expected_comment_kwargs)

    @skip("TODO")
    @mock.patch("email_router.ses_email_receiving.email_utils.Zenpy")
    @mock.patch("email_router.ses_email_receiving.email_utils.Comment")
    @mock.patch("email_router.ses_email_receiving.email_utils.User")
    @mock.patch("email_router.ses_email_receiving.email_utils.Ticket")
    def test_create_ticket_creates_zenpy_ticket(
        self,
        mock_ticket: MagicMock,
        mock_user: MagicMock,
        mock_comment: MagicMock,
        mock_zenpy: MagicMock,
        parsed_email_sans_attachments,
    ):
        mock_zenpy.return_value = MagicMock()
        mock_comment.return_value = MagicMock()
        mock_user.return_value = MagicMock()
        zendesk_email = "test@example.com"  # /PS-IGNORE
        zendesk_token = "test123"
        api_client = MicroserviceAPIClient(zendesk_email, zendesk_token)
        expected_ticket_kwargs = {
            "subject": f"{parsed_email_sans_attachments.subject} via netloc not found",
            "comment": mock_comment.return_value,
            "requester": mock_user.return_value,
            "recipient": parseaddr(parsed_email_sans_attachments.recipient)[1],
        }

        api_client.create_ticket(parsed_email_sans_attachments)

        mock_ticket.assert_called_once_with(**expected_ticket_kwargs)

    @skip("TODO")
    @mock.patch("email_router.ses_email_receiving.email_utils.Zenpy")
    @mock.patch("email_router.ses_email_receiving.email_utils.Comment")
    @mock.patch("email_router.ses_email_receiving.email_utils.User")
    @mock.patch("email_router.ses_email_receiving.email_utils.Ticket")
    def test_create_ticket_calls_ticket_create(
        self,
        mock_ticket: MagicMock,
        mock_user: MagicMock,
        mock_comment: MagicMock,
        mock_zenpy: MagicMock,
        parsed_email_sans_attachments,
    ):
        mock_zenpy_client = MagicMock()
        mock_zenpy.return_value = mock_zenpy_client
        mock_comment.return_value = MagicMock()
        mock_user.return_value = MagicMock()
        mock_ticket.return_value = MagicMock()
        zendesk_email = "test@example.com"  # /PS-IGNORE
        zendesk_token = "test123"
        api_client = MicroserviceAPIClient(zendesk_email, zendesk_token)
        expected_ticket_create_arg = mock_ticket.return_value

        api_client.create_ticket(parsed_email_sans_attachments)

        mock_zenpy_client.tickets.create.assert_called_once_with(expected_ticket_create_arg)

    @skip("TODO")
    @mock.patch("email_router.ses_email_receiving.email_utils.Zenpy")
    def test_upload_attachment_calls_attachments_upload(self, mock_zenpy: MagicMock):
        mock_zenpy_client = MagicMock()
        mock_zenpy.return_value = mock_zenpy_client
        zendesk_email = "test@example.com"  # /PS-IGNORE
        zendesk_token = "test123"
        api_client = MicroserviceAPIClient(zendesk_email, zendesk_token)
        expected_payload = "test"
        expected_filename = "test.txt"
        expected_content_type = "text/plain"

        api_client.upload_attachment(
            payload=expected_payload,
            target_name=expected_filename,
            content_type=expected_content_type,
        )

        mock_zenpy_client.attachments.upload.assert_called_once_with(
            expected_payload, target_name=expected_filename, content_type=expected_content_type
        )

    @skip("TODO")
    @mock.patch("email_router.ses_email_receiving.email_utils.Zenpy")
    def test_upload_attachments_makes_zenpy_uploads(self, mock_zenpy: MagicMock):
        mock_zenpy_client = MagicMock()
        mock_zenpy.return_value = mock_zenpy_client
        zendesk_email = "test@example.com"  # /PS-IGNORE
        zendesk_token = "test123"
        api_client = MicroserviceAPIClient(zendesk_email, zendesk_token)
        uploads = [
            {"payload": "text one", "filename": "textfile.txt", "content_type": "text/plain"},
            {
                "payload": b"binary one",
                "filename": "binaryfile.bin",
                "content_type": "application/octet-stream",
            },
        ]
        expected_upload_tokens = [123, 321]
        upload_objects = [Upload(token=token) for token in expected_upload_tokens]
        mock_zenpy_client.attachments.upload.side_effect = upload_objects
        expected_calls = [
            call(
                upload["payload"],
                target_name=upload["filename"],
                content_type=upload["content_type"],
            )
            for upload in uploads
        ]

        api_client.upload_attachments(uploads)

        assert mock_zenpy_client.attachments.upload.call_count == len(expected_calls)
        mock_zenpy_client.attachments.upload.assert_has_calls(expected_calls)

    @skip("TODO")
    @mock.patch("email_router.ses_email_receiving.email_utils.Zenpy")
    def test_upload_attachments_returns_upload_tokens(self, mock_zenpy: MagicMock):
        mock_zenpy_client = MagicMock()
        mock_zenpy.return_value = mock_zenpy_client
        zendesk_email = "test@example.com"  # /PS-IGNORE
        zendesk_token = "test123"
        api_client = MicroserviceAPIClient(zendesk_email, zendesk_token)
        uploads = [
            {"payload": "text one", "filename": "textfile.txt", "content_type": "text/plain"},
            {
                "payload": b"binary one",
                "filename": "binaryfile.bin",
                "content_type": "application/octet-stream",
            },
        ]
        expected_upload_tokens = [123, 321]
        upload_objects = [Upload(token=token) for token in expected_upload_tokens]
        mock_zenpy_client.attachments.upload.side_effect = upload_objects

        upload_tokens = api_client.upload_attachments(uploads)

        assert upload_tokens == expected_upload_tokens

    @skip("TODO")
    @mock.patch("email_router.ses_email_receiving.email_utils.MicroserviceAPIClient.create_ticket")
    @mock.patch(
        "email_router.ses_email_receiving.email_utils.MicroserviceAPIClient.upload_attachments"
    )
    def test_create_ticket_from_message_performs_uploads_and_creates_tickets(
        self, mock_upload_attachments: MagicMock, mock_create_ticket: MagicMock, parsed_email
    ):
        mock_upload_attachments.return_value = [123, 321]
        mock_create_ticket.return_value = {}
        zendesk_email = "test@example.com"  # /PS-IGNORE
        zendesk_token = "test123"
        api_client = MicroserviceAPIClient(zendesk_email, zendesk_token)

        api_client.create_or_update_ticket_from_message(parsed_email)

        mock_upload_attachments.assert_called_once()
        mock_create_ticket.assert_called_once()

    @skip("TODO")
    @mock.patch("email_router.ses_email_receiving.email_utils.MicroserviceAPIClient.create_ticket")
    @mock.patch("email_router.ses_email_receiving.email_utils.MicroserviceAPIClient.update_ticket")
    def test_update_ticket_from_message_does_not_create_ticket(
        self,
        _mock_update_ticket: MagicMock,
        mock_create_ticket: MagicMock,
        parsed_reply_to_ticket_email,
    ):
        mock_create_ticket.return_value = {}
        zendesk_email = "test@example.com"  # /PS-IGNORE
        zendesk_token = "test123"
        api_client = MicroserviceAPIClient(zendesk_email, zendesk_token)

        api_client.create_or_update_ticket_from_message(parsed_reply_to_ticket_email)

        mock_create_ticket.assert_not_called()

    @skip("TODO")
    @mock.patch("email_router.ses_email_receiving.email_utils.MicroserviceAPIClient.create_ticket")
    @mock.patch("email_router.ses_email_receiving.email_utils.MicroserviceAPIClient.update_ticket")
    def test_update_ticket_from_message_adds_comment_to_ticket(
        self,
        mock_update_ticket: MagicMock,
        _mock_create_ticket: MagicMock,
        parsed_reply_to_ticket_email,
    ):
        mock_update_ticket.return_value = {}
        zendesk_email = "test@example.com"  # /PS-IGNORE
        zendesk_token = "test123"
        api_client = MicroserviceAPIClient(zendesk_email, zendesk_token)

        api_client.create_or_update_ticket_from_message(parsed_reply_to_ticket_email)

        mock_update_ticket.assert_called_once()
