from http import HTTPStatus
from unittest import mock

from django.test import Client
from django.urls import reverse
from requests import Response


class TestSupportedOperations:
    """
    The following @mock.patch lines ensure the external services don't actually
    have requests made to them by the test.
    """

    @mock.patch("zendesk_api_proxy.middleware.proxy_zendesk")
    def test_get_ticket_by_id(
        self,
        proxy_zendesk: mock.MagicMock,
        client: Client,
        zendesk_required_settings,  # fixture: see /tests/conftest.py
        zendesk_creds_only,
        zendesk_authorization_header,
    ):
        url = reverse("api:ticket", kwargs={"id": 123})

        response = Response()
        response._content = b"{}"
        response.status_code = HTTPStatus.OK

        proxy_zendesk.return_value = response
        client.get(url, headers={"Authorization": zendesk_authorization_header})
        proxy_zendesk.assert_called_once()

        request_obj, subdomain, email, *_ = proxy_zendesk.call_args[0]  # args passed to proxy_zendesk

        assert request_obj.get_full_path() == url
        assert request_obj.method == "GET"
        assert subdomain == zendesk_creds_only.zendesk_subdomain
        assert email == zendesk_creds_only.zendesk_email
        

    @mock.patch("zendesk_api_proxy.middleware.proxy_zendesk")
    def test_post_ticket(
        self,
        proxy_zendesk: mock.MagicMock,
        client: Client,
        zendesk_required_settings,  # fixture: see /tests/conftest.py
        zendesk_creds_only,
        zendesk_authorization_header,
    ):
        url = reverse("api:tickets")

        response = Response()
        response._content = b"{}"
        response.status_code = HTTPStatus.OK

        proxy_zendesk.return_value = response
        client.post(url, headers={"Authorization": zendesk_authorization_header})
        proxy_zendesk.assert_called_once()

        request_obj, subdomain, email, *_ = proxy_zendesk.call_args[0]  # args passed to proxy_zendesk

        assert request_obj.get_full_path() == url
        assert request_obj.method == "POST"
        assert subdomain == zendesk_creds_only.zendesk_subdomain
        assert email == zendesk_creds_only.zendesk_email
