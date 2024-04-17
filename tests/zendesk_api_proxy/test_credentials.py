from http import HTTPStatus
from unittest import mock
from unittest.mock import MagicMock

import pytest
from django.http import HttpResponse, JsonResponse
from django.test import Client, RequestFactory
from django.urls import reverse
from rest_framework.exceptions import AuthenticationFailed
from zendesk_api_proxy.middleware import ZendeskAPIProxyMiddleware

from help_desk_api.models import HelpDeskCreds


class TestCredentials:
    """/PS-IGNORE
    The credentials system relies on an email address and Zendesk token
    encoded in a request's Authorization header.
    The header is deconstructed to obtain the values of these
    and confirm that a corresponding record is present
    as a HelpDeskCreds object.
    If such a record exists, these credentials are then used directly
    to connect to the Zendesk API.
    For Halo, the Client ID and Secret are held
    in the HelpDeskCreds object.
    """

    def test_get_zenpy_request_vars(
        self, rf: RequestFactory, zendesk_authorization_header: str, zendesk_email, zendesk_token
    ):
        request = rf.get(reverse("api:tickets"), HTTP_AUTHORIZATION=zendesk_authorization_header)
        from help_desk_api.utils import get_zenpy_request_vars

        token, email = get_zenpy_request_vars(request)

        assert token == zendesk_token
        assert email == zendesk_email

    def test_unknown_email_address_raises_401_unauthorized(
        self, rf: RequestFactory, unknown_email_zendesk_authorization_header: str
    ):
        request = rf.get(
            reverse("api:tickets"), HTTP_AUTHORIZATION=unknown_email_zendesk_authorization_header
        )
        mock_get_response = MagicMock()
        middleware = ZendeskAPIProxyMiddleware(mock_get_response)

        with pytest.raises(AuthenticationFailed):
            middleware(request)

    def test_incorrect_token_raises_401_unauthorized(
        self, rf: RequestFactory, incorrect_token_zendesk_authorization_header: str
    ):
        request = rf.get(
            reverse("api:tickets"), HTTP_AUTHORIZATION=incorrect_token_zendesk_authorization_header
        )
        mock_get_response = MagicMock()
        middleware = ZendeskAPIProxyMiddleware(mock_get_response)

        with pytest.raises(AuthenticationFailed):
            middleware(request)

    @mock.patch("help_desk_api.views.HaloManager")
    @mock.patch("help_desk_api.views.HaloBaseView.initial")
    def test_api_request_lacking_authorization_header_blocked_from_api_view(
        self, mock_api_view_initial: MagicMock, mock_halo_manager: MagicMock, client: Client
    ):
        url = reverse("api:ticket", kwargs={"id": 123})

        client.get(
            url,
            data={},
            content_type="application/json",
        )

        mock_api_view_initial.assert_not_called()
        mock_halo_manager.assert_not_called()

    def test_api_request_lacking_authorization_header_returns_401_unauthorized(
        self, client: Client
    ):
        url = reverse("api:ticket", kwargs={"id": 123})

        response: HttpResponse = client.get(
            url,
            data={},
            content_type="application/json",
        )

        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_api_request_lacking_authorization_header_returns_zendesk_error_content(
        self, client: Client
    ):
        url = reverse("api:ticket", kwargs={"id": 123})

        response: JsonResponse = client.get(
            url,
            data={},
            content_type="application/json",
        )

        response_content = response.json()
        assert "error" in response_content
        assert response_content["error"] == "Couldn't authenticate you"

    @mock.patch("help_desk_api.views.SingleTicketView.get")
    @mock.patch("help_desk_api.views.HaloManager")
    def test_api_request_with_authorization_header_reaches_api_view(
        self,
        mock_halo_manager: MagicMock,
        mock_ticket_view_get: MagicMock,
        client: Client,
        halo_creds_only: HelpDeskCreds,
        zendesk_authorization_header: str,
        zendesk_create_ticket_response: HttpResponse,
    ):
        url = reverse("api:ticket", kwargs={"id": 123})
        mock_halo_manager_instance = MagicMock()
        mock_halo_manager.return_value = mock_halo_manager_instance
        mock_ticket_view_get.return_value = zendesk_create_ticket_response

        client.get(
            url,
            data={},
            content_type="application/json",
            headers={"Authorization": zendesk_authorization_header},
        )

        mock_halo_manager.assert_called_once()
        mock_ticket_view_get.assert_called_once()
