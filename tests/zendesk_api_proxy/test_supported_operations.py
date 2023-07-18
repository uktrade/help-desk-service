from http import HTTPStatus
from unittest import mock
import pytest

from django.test import Client
from django.urls import reverse
from requests import Response
from zendesk_api_proxy.middleware import get_view_class
from zendesk_api_proxy.middleware import method_supported


class TestSupportedOperations:
    # †est different path/view_class scenarios by using the @pytest.mark.parametrize decorator
    @pytest.mark.parametrize(
        "path, view_class",
        [
            ("/api/v2/users/123.json", "help_desk_api.views.UserView"),
            ("/api/v2/tickets/123.json", "help_desk_api.views.TicketView"),
            ("/api/v2/tickets/123/comments.json", "help_desk_api.views.CommentView"),
            ("/api/v2/users/me.json", "help_desk_api.views.MeView"),
        ],
    )
    def test_get_view_class_correct(self, path, view_class):
        assert get_view_class(path) == view_class

    # some fake paths
    @pytest.mark.parametrize(
        "path, view_class",
        [
            ("/api/fake/users/123.json", "help_desk_api.views.UserView"),
            ("/api/fake/tickets/123.json", "help_desk_api.views.TicketView"),
            ("/api/fake/tickets/123/comments.json", "help_desk_api.views.CommentView"),
            ("/api/fake/users/me.json", "help_desk_api.views.MeView"),
        ],
    )
    def test_get_view_class_not_correct_paths(self, path, view_class):
        assert not get_view_class(path) == view_class

    # †est different path/method scenarios by using the @pytest.mark.parametrize decorator
    @pytest.mark.parametrize(
        "path, method",
        [
            ("/api/v2/users/123.json", "GET"),
            ("/api/v2/tickets/123.json", "POST"),
            ("/api/v2/tickets/123/comments.json", "GET"),
            ("/api/v2/users/me.json", "GET"),
        ],
    )
    def test_method_supported_success(self, path, method):
        assert method_supported(path, method)

    # †est some fake path/method scenarios
    @pytest.mark.parametrize(
        "path, method",
        [
            ("/api/fake/users/123.json", "GET"),
            ("/api/fake/tickets/123.json", "POST"),
            ("/api/v2/tickets/123/comments.json", "POST"),
            ("/api/v2/users/me.json", "PUT"),
        ],
    )
    def test_method_supported_fake_paths_methods(self, path, method):
        assert not method_supported(path, method)

    """
    The following @mock.patch lines ensure the external services don't actually
    have requests made to them by the test.
    """

    # †est different url scenarios in get by using the @pytest.mark.parametrize decorator
    @pytest.mark.parametrize(
        "url",
        [
            (reverse("api:ticket", kwargs={"id": 123})),
            (reverse("api:comments", kwargs={"id": 123})),
            (reverse("api:user", kwargs={"id": 123})),
            (reverse("api:me")),
        ],
    )
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

        request_obj, subdomain, email, *_ = proxy_zendesk.call_args[
            0
        ]  # args passed to proxy_zendesk

        assert request_obj.get_full_path() == url
        assert request_obj.method == "GET"
        assert subdomain == zendesk_creds_only.zendesk_subdomain
        assert email == zendesk_creds_only.zendesk_email

    @pytest.mark.parametrize(
        "url",
        [
            (reverse("api:tickets")),
        ],
    )
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

        request_obj, subdomain, email, *_ = proxy_zendesk.call_args[
            0
        ]  # args passed to proxy_zendesk

        assert request_obj.get_full_path() == url
        assert request_obj.method == "POST"
        assert subdomain == zendesk_creds_only.zendesk_subdomain
        assert email == zendesk_creds_only.zendesk_email

    # Testing PUT
    @pytest.mark.parametrize(
        "url",
        [
            (reverse("api:ticket", kwargs={"id": 123})),
        ],
    )
    @mock.patch("zendesk_api_proxy.middleware.proxy_zendesk")
    def test_update_ticket_by_id(
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
        client.put(url, headers={"Authorization": zendesk_authorization_header})
        proxy_zendesk.assert_called_once()

        request_obj, subdomain, email, *_ = proxy_zendesk.call_args[
            0
        ]  # args passed to proxy_zendesk

        assert request_obj.get_full_path() == url
        assert request_obj.method == "PUT"
        assert request_obj.body.decode("utf8") == ""
        assert subdomain == zendesk_creds_only.zendesk_subdomain
        assert email == zendesk_creds_only.zendesk_email
