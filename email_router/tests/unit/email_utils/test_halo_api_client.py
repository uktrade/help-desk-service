import base64
import json
from http import HTTPStatus
from unittest import mock
from unittest.mock import MagicMock

from email_router.ses_email_receiving.email_utils import HaloAPIClient, ParsedEmail
from requests import Response


@mock.patch("email_router.ses_email_receiving.email_utils.requests.post")
class TestHaloAPIClientAuthentication:
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
        "email_router.ses_email_receiving.email_utils.HaloAPIClient._HaloAPIClient__authenticate",
        return_value="123abc",
    )
    def test_api_client_authenticates(self, mock_authenticate: MagicMock, _mock_post: MagicMock):
        halo_subdomain = "foo"
        halo_client_id = "abcdef"  # /PS-IGNORE
        halo_client_secret = "123456"
        expected_kwargs = {
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


@mock.patch(
    "email_router.ses_email_receiving.email_utils.HaloAPIClient._HaloAPIClient__authenticate",
    return_value="123abc",
)
class TestHaloAPIClientTicketRequestData:
    def test_halo_request_data_from_message_is_in_list(
        self, _mock_authenticate: MagicMock, parsed_plain_text_email, halo_api_client
    ):
        halo_request_data = halo_api_client.halo_ticket_data_from_message(parsed_plain_text_email)

        assert isinstance(halo_request_data, list)

    def test_halo_request_data_from_message_is_dict(
        self, _mock_authenticate: MagicMock, parsed_plain_text_email, halo_api_client
    ):
        wrapped_halo_request_data = halo_api_client.halo_ticket_data_from_message(
            parsed_plain_text_email
        )
        halo_request_data = wrapped_halo_request_data[0]

        assert isinstance(halo_request_data, dict)

    def test_halo_request_data_from_message_has_summary(
        self, _mock_authenticate: MagicMock, parsed_plain_text_email, halo_api_client
    ):
        wrapped_halo_request_data = halo_api_client.halo_ticket_data_from_message(
            parsed_plain_text_email
        )
        halo_request_data = wrapped_halo_request_data[0]

        summary = halo_request_data.get("summary")
        assert summary == parsed_plain_text_email.subject

    def test_halo_request_data_from_message_has_details(
        self, _mock_authenticate: MagicMock, parsed_plain_text_email, halo_api_client
    ):
        wrapped_halo_request_data = halo_api_client.halo_ticket_data_from_message(
            parsed_plain_text_email
        )
        halo_request_data = wrapped_halo_request_data[0]

        details = halo_request_data.get("details_html")
        assert details == parsed_plain_text_email.payload

    def test_halo_request_data_from_message_has_users_name(
        self, _mock_authenticate: MagicMock, parsed_plain_text_email, halo_api_client
    ):
        wrapped_halo_request_data = halo_api_client.halo_ticket_data_from_message(
            parsed_plain_text_email
        )
        halo_request_data = wrapped_halo_request_data[0]

        users_name = halo_request_data.get("users_name")
        assert users_name == parsed_plain_text_email.sender_name

    def test_halo_request_data_from_message_has_reportedby(
        self, _mock_authenticate: MagicMock, parsed_plain_text_email, halo_api_client
    ):
        wrapped_halo_request_data = halo_api_client.halo_ticket_data_from_message(
            parsed_plain_text_email
        )
        halo_request_data = wrapped_halo_request_data[0]

        reportedby = halo_request_data.get("reportedby")
        assert reportedby == parsed_plain_text_email.sender_email

    def test_halo_request_data_from_message_has_tickettype_id(
        self, _mock_authenticate: MagicMock, parsed_plain_text_email, halo_api_client
    ):
        wrapped_halo_request_data = halo_api_client.halo_ticket_data_from_message(
            parsed_plain_text_email
        )
        halo_request_data = wrapped_halo_request_data[0]

        tickettype_id = halo_request_data.get("tickettype_id")
        assert tickettype_id == 36

    def test_halo_request_data_from_message_has_dont_do_rules(
        self, _mock_authenticate: MagicMock, parsed_plain_text_email, halo_api_client
    ):
        wrapped_halo_request_data = halo_api_client.halo_ticket_data_from_message(
            parsed_plain_text_email
        )
        halo_request_data = wrapped_halo_request_data[0]

        dont_do_rules = halo_request_data.get("dont_do_rules")
        assert dont_do_rules is False

    def test_halo_request_data_from_message_has_no_attachments_if_not_present(
        self, _mock_authenticate: MagicMock, parsed_plain_text_email, halo_api_client
    ):
        wrapped_halo_request_data = halo_api_client.halo_ticket_data_from_message(
            parsed_plain_text_email
        )
        halo_request_data = wrapped_halo_request_data[0]

        assert "attachments" not in halo_request_data

    def test_halo_request_data_from_message_has_attachments_if_present(
        self, _mock_authenticate: MagicMock, parsed_plain_text_email, halo_api_client
    ):
        upload_tokens = [1, 2, 3]
        expected_attachments = [{"id": upload_token} for upload_token in upload_tokens]

        wrapped_halo_request_data = halo_api_client.halo_ticket_data_from_message(
            parsed_plain_text_email, upload_tokens=upload_tokens
        )
        halo_request_data = wrapped_halo_request_data[0]

        assert "attachments" in halo_request_data
        assert halo_request_data["attachments"] == expected_attachments

    def test_halo_request_data_from_message_has_to_address_in_custom_field(
        self, _mock_authenticate: MagicMock, parsed_plain_text_email, halo_api_client
    ):
        wrapped_halo_request_data = halo_api_client.halo_ticket_data_from_message(
            parsed_plain_text_email
        )
        halo_request_data = wrapped_halo_request_data[0]

        custom_fields = halo_request_data.get(
            "customfields",
            [
                {},
            ],
        )
        custom_field = custom_fields[0]
        custom_field_name = custom_field.get("name", None)
        custom_field_value = custom_field.get("value", None)

        assert custom_field_name == "CFEmailToAddress"
        assert custom_field_value == parsed_plain_text_email.recipient


@mock.patch("email_router.ses_email_receiving.email_utils.requests.post")
class TestHaloAPIClientCreateTicket:

    def test_halo_client_posts_message_as_ticket(
        self,
        mock_post: MagicMock,
        halo_create_ticket_response,
        parsed_plain_text_email,
        halo_api_client,
    ):
        halo_subdomain = halo_api_client.halo_subdomain
        mock_post.return_value = halo_create_ticket_response
        expected_url = f"https://{halo_subdomain}.haloitsm.com/api/Tickets"
        expected_ticket_data = json.dumps(
            halo_api_client.halo_ticket_data_from_message(parsed_plain_text_email)
        )
        expected_headers = {
            "Authorization": f"Bearer {halo_api_client.halo_token}",
            "Content-Type": "application/json",
        }
        expected_kwargs = {
            "data": expected_ticket_data,
            "headers": expected_headers,
        }

        halo_api_client.create_ticket(parsed_plain_text_email, [])

        mock_post.assert_called_once_with(expected_url, **expected_kwargs)


@mock.patch("email_router.ses_email_receiving.email_utils.requests.post")
@mock.patch(
    "email_router.ses_email_receiving.email_utils.HaloAPIClient._HaloAPIClient__authenticate",
    return_value="123abc",
)
class TestHaloAPIClientTicketAttachments:
    @mock.patch("email_router.ses_email_receiving.email_utils.HaloAPIClient.upload_attachment")
    def test_email_with_attachment_calls_upload_attachment(
        self,
        mock_upload_attachment: MagicMock,
        _mock_authenticate: MagicMock,
        mock_post: MagicMock,
        parsed_email_single_attachment: ParsedEmail,
        halo_create_ticket_response,
        halo_api_client,
    ):
        mock_post.return_value = halo_create_ticket_response
        mock_upload_attachment.return_value = HaloAPIClient.Upload(token=123)
        attachment = list(parsed_email_single_attachment.attachments)[0]
        expected_kwargs = {
            "payload": attachment["payload"],
            "target_name": attachment["filename"],
            "content_type": attachment["content_type"],
        }

        halo_api_client.create_or_update_ticket_from_message(parsed_email_single_attachment)

        assert mock_upload_attachment.called_once_with(**expected_kwargs)

    @mock.patch("email_router.ses_email_receiving.email_utils.HaloAPIClient.create_ticket")
    def test_upload_attachment_payload(
        self,
        _mock_create_ticket: MagicMock,
        _mock_authenticate: MagicMock,
        mock_post: MagicMock,
        halo_upload_response,
        parsed_email_single_attachment: ParsedEmail,
        halo_api_client: HaloAPIClient,
    ):
        mock_post.return_value = halo_upload_response
        attachment = list(parsed_email_single_attachment.attachments)[0]
        filename = attachment["filename"]
        content_type = attachment["content_type"]
        data = attachment["payload"]
        file_content_base64 = base64.b64encode(data).decode("ascii")  # /PS-IGNORE
        payload = f"data:{content_type};base64,{file_content_base64}"  # noqa: E231,E702
        expected_data = [
            {
                "filename": filename,
                "isimage": content_type.startswith("image"),
                "data_base64": payload,  # /PS-IGNORE
            }
        ]
        expected_post_data = json.dumps(expected_data)
        expected_url = f"https://{halo_api_client.halo_subdomain}.haloitsm.com/api/Attachment"
        expected_headers = {
            "Authorization": f"Bearer {halo_api_client.halo_token}",
            "Content-Type": "application/json",
        }

        halo_api_client.create_or_update_ticket_from_message(parsed_email_single_attachment)

        mock_post.assert_called_once_with(
            expected_url, data=expected_post_data, headers=expected_headers
        )


@mock.patch("email_router.ses_email_receiving.email_utils.requests.post")
@mock.patch(
    "email_router.ses_email_receiving.email_utils.HaloAPIClient._HaloAPIClient__authenticate"
)
class TestHaloAPIClientUpdateTicket:
    @mock.patch("email_router.ses_email_receiving.email_utils.HaloAPIClient.update_ticket")
    def test_reply_to_ticket_delegates_to_update_ticket(
        self,
        mock_update_ticket: MagicMock,
        _mock_authenticate: MagicMock,
        _mock_post: MagicMock,
        halo_create_ticket_response: Response,
        parsed_reply_to_ticket_email: ParsedEmail,
        halo_api_client: HaloAPIClient,
    ):
        halo_api_client.create_or_update_ticket_from_message(parsed_reply_to_ticket_email)

        mock_update_ticket.assert_called_once()

    def test_update_ticket_makes_correct_halo_request(
        self,
        _mock_authenticate: MagicMock,
        mock_post: MagicMock,
        halo_create_ticket_response: Response,
        parsed_reply_to_ticket_email: ParsedEmail,
        halo_api_client: HaloAPIClient,
    ):
        mock_post.return_value = halo_create_ticket_response
        halo_subdomain = halo_api_client.halo_subdomain
        expected_url = f"https://{halo_subdomain}.haloitsm.com/api/Actions"
        expected_ticket_id = parsed_reply_to_ticket_email.reply_to_ticket_id
        expected_ticket_data = json.dumps(
            halo_api_client.halo_action_data_from_message(
                parsed_reply_to_ticket_email, ticket_id=expected_ticket_id
            )
        )
        expected_headers = {
            "Authorization": f"Bearer {halo_api_client.halo_token}",
            "Content-Type": "application/json",
        }
        expected_kwargs = {
            "data": expected_ticket_data,
            "headers": expected_headers,
        }

        halo_api_client.update_ticket(
            parsed_reply_to_ticket_email, [], parsed_reply_to_ticket_email.reply_to_ticket_id
        )

        mock_post.assert_called_once_with(expected_url, **expected_kwargs)
