from http import HTTPStatus
from unittest import mock
from unittest.mock import MagicMock

from django.http import HttpResponse
from django.urls import reverse


@mock.patch("halo.halo_manager.HaloAPIClient._HaloAPIClient__authenticate", return_value="abc123")
@mock.patch("zendesk_api_proxy.middleware.ZendeskAPIProxyMiddleware.make_zendesk_request")
@mock.patch("zendesk_api_proxy.middleware.ZendeskAPIProxyMiddleware.make_halo_request")
class TestDualRunningExceptionHandling:
    def test_dual_running_halo_error_allows_valid_zendesk_response(
        self,
        mock_make_halo_request: MagicMock,
        mock_make_zendesk_request: MagicMock,
        _mock_halo_authenticate: MagicMock,
        zendesk_create_ticket_request,
        zendesk_create_ticket_response,
        zendesk_authorization_header,
        zendesk_and_halo_creds,
        client,
    ):
        mock_make_zendesk_request.return_value = zendesk_create_ticket_response
        mock_make_halo_request.side_effect = Exception("Test Halo error")
        url = reverse("api:tickets")

        response: HttpResponse = client.post(
            url,
            data=zendesk_create_ticket_request,
            headers={"Authorization": zendesk_authorization_header},
            content_type="application/json",
        )

        assert response.status_code == HTTPStatus.CREATED

    def test_single_running_halo_error_returns_error_response(
        self,
        mock_make_halo_request: MagicMock,
        mock_make_zendesk_request: MagicMock,
        _mock_halo_authenticate: MagicMock,
        zendesk_create_ticket_request,
        zendesk_create_ticket_response,
        zendesk_authorization_header,
        halo_creds_only,
        client,
    ):
        mock_make_zendesk_request.return_value = zendesk_create_ticket_response
        mock_make_halo_request.side_effect = Exception("Test Halo error")
        url = reverse("api:tickets")

        response: HttpResponse = client.post(
            url,
            data=zendesk_create_ticket_request,
            headers={"Authorization": zendesk_authorization_header},
            content_type="application/json",
        )

        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
