from http import HTTPStatus
from unittest import mock
import pytest

from django.test import Client
from django.urls import reverse
from requests import Response


class TestSupportedOperations:
    """
    The following @mock.patch lines ensure the external services don't actually
    have requests made to them by the test.
    """
    
    # †est different url scenarios in get by using the @pytest.mark.parametrize decorator
    @pytest.mark.parametrize("url", [
                (reverse("api:ticket", kwargs={"id": 123})),
                (reverse("api:comments", kwargs={"id": 123})),
                (reverse("api:user", kwargs={"id": 123})),
                (reverse("api:me")),
    ])
    @mock.patch("zendesk_api_proxy.middleware.proxy_zendesk")
    def test_get_ticket_user_by_id(
        self,
        proxy_zendesk: mock.MagicMock,
        client: Client,
        zendesk_required_settings,  # fixture: see /tests/conftest.py
        zendesk_creds_only,
        zendesk_authorization_header,
        url,
    ):

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


    @pytest.mark.parametrize("url", [
                (reverse("api:tickets")),
    ])
    @mock.patch("zendesk_api_proxy.middleware.proxy_zendesk")
    def test_post_ticket(
        self,
        proxy_zendesk: mock.MagicMock,
        client: Client,
        zendesk_required_settings,  # fixture: see /tests/conftest.py
        zendesk_creds_only,
        zendesk_authorization_header,
        url,
    ):

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

