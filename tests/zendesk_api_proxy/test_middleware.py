import json
from http import HTTPStatus
from unittest import mock
from unittest.mock import MagicMock

import pytest
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.test import RequestFactory
from django.urls import reverse
from zendesk_api_proxy.middleware import ZendeskAPIProxyMiddleware

from help_desk_api.models import HelpDeskCreds


class TestNonApiRoutes:
    @mock.patch("zendesk_api_proxy.middleware.ZendeskAPIProxyMiddleware.make_zendesk_request")
    @mock.patch("zendesk_api_proxy.middleware.ZendeskAPIProxyMiddleware.make_halo_request")
    def test_non_api_call_passed_through(
        self,
        make_halo_request: mock.MagicMock,
        make_zendesk_request: mock.MagicMock,
        rf: RequestFactory,
        zendesk_required_settings,
    ):
        get_response = mock.MagicMock()
        middleware = ZendeskAPIProxyMiddleware(get_response)
        request = rf.get("/")

        middleware(request)

        get_response.assert_called_once_with(request)


class TestZendeskOnly:
    @mock.patch("zendesk_api_proxy.middleware.ZendeskAPIProxyMiddleware.make_zendesk_request")
    @mock.patch("zendesk_api_proxy.middleware.ZendeskAPIProxyMiddleware.make_halo_request")
    def test_zendesk_request_calls_make_zendesk_request(
        self,
        make_halo_request: mock.MagicMock,
        make_zendesk_request: mock.MagicMock,
        zendesk_authorization_header: str,
        rf: RequestFactory,
        zendesk_required_settings,
        zendesk_creds_only: HelpDeskCreds,
    ):
        def get_response():
            pass

        middleware = ZendeskAPIProxyMiddleware(get_response)
        ticket = {
            "subject": "Test ticket subject",
            "description": "Test ticket description",
            "user": "",
        }
        request = rf.post(
            reverse("api:tickets"), data=ticket, HTTP_AUTHORIZATION=zendesk_authorization_header
        )

        middleware(request)

        make_zendesk_request.assert_called_once()

    @mock.patch("zendesk_api_proxy.middleware.ZendeskAPIProxyMiddleware.make_zendesk_request")
    @mock.patch("zendesk_api_proxy.middleware.ZendeskAPIProxyMiddleware.make_halo_request")
    def test_zendesk_request_does_not_call_make_halo_request(
        self,
        make_halo_request: mock.MagicMock,
        make_zendesk_request: mock.MagicMock,
        zendesk_authorization_header: str,
        rf: RequestFactory,
        zendesk_required_settings,
        zendesk_creds_only: HelpDeskCreds,
    ):
        def get_response():
            pass

        middleware = ZendeskAPIProxyMiddleware(get_response)
        ticket = {
            "subject": "Test ticket subject",
            "description": "Test ticket description",
            "user": "",
        }
        request = rf.post(
            reverse("api:tickets"), data=ticket, HTTP_AUTHORIZATION=zendesk_authorization_header
        )

        middleware(request)

        make_halo_request.assert_not_called()

    @mock.patch("zendesk_api_proxy.middleware.ZendeskAPIProxyMiddleware.make_zendesk_request")
    @mock.patch("zendesk_api_proxy.middleware.ZendeskAPIProxyMiddleware.make_halo_request")
    def test_zendesk_request_does_not_call_get_response(
        self,
        make_halo_request: mock.MagicMock,
        make_zendesk_request: mock.MagicMock,
        zendesk_authorization_header: str,
        rf: RequestFactory,
        zendesk_required_settings,
        zendesk_creds_only: HelpDeskCreds,
    ):
        get_response = mock.MagicMock()
        middleware = ZendeskAPIProxyMiddleware(get_response)
        ticket = {
            "subject": "Test ticket subject",
            "description": "Test ticket description",
            "user": "",
        }
        request = rf.post(
            reverse("api:tickets"), data=ticket, HTTP_AUTHORIZATION=zendesk_authorization_header
        )

        middleware(request)

        get_response.assert_not_called()

    def test_get_zenpy_request_vars(
        self, rf: RequestFactory, zendesk_authorization_header: str, zendesk_email, zendesk_token
    ):
        request = rf.get(reverse("api:tickets"), HTTP_AUTHORIZATION=zendesk_authorization_header)
        from help_desk_api.utils import get_zenpy_request_vars

        token, email = get_zenpy_request_vars(request)

        assert token == zendesk_token
        assert email == zendesk_email


class TestHaloOnly:
    @mock.patch("zendesk_api_proxy.middleware.ZendeskAPIProxyMiddleware.make_zendesk_request")
    @mock.patch("zendesk_api_proxy.middleware.ZendeskAPIProxyMiddleware.make_halo_request")
    def test_halo_request_calls_make_halo_request(
        self,
        make_halo_request: mock.MagicMock,
        make_zendesk_request: mock.MagicMock,
        zendesk_authorization_header: str,
        rf: RequestFactory,
        zendesk_not_required_settings,
        halo_creds_only: HelpDeskCreds,
    ):
        def get_response():
            pass

        middleware = ZendeskAPIProxyMiddleware(get_response)
        ticket = {
            "subject": "Test ticket subject",
            "description": "Test ticket description",
            "user": "",
        }
        request = rf.post(
            reverse("api:tickets"), data=ticket, HTTP_AUTHORIZATION=zendesk_authorization_header
        )

        middleware(request)

        make_halo_request.assert_called_once()

    @mock.patch("zendesk_api_proxy.middleware.ZendeskAPIProxyMiddleware.make_zendesk_request")
    @mock.patch("zendesk_api_proxy.middleware.ZendeskAPIProxyMiddleware.make_halo_request")
    def test_halo_request_does_not_call_make_zendesk_request(
        self,
        make_halo_request: mock.MagicMock,
        make_zendesk_request: mock.MagicMock,
        zendesk_authorization_header: str,
        rf: RequestFactory,
        zendesk_not_required_settings,
        halo_creds_only: HelpDeskCreds,
    ):
        def get_response():
            pass

        middleware = ZendeskAPIProxyMiddleware(get_response)
        ticket = {
            "subject": "Test ticket subject",
            "description": "Test ticket description",
            "user": "",
        }
        request = rf.post(
            reverse("api:tickets"), data=ticket, HTTP_AUTHORIZATION=zendesk_authorization_header
        )

        middleware(request)

        make_zendesk_request.assert_not_called()

    @mock.patch("zendesk_api_proxy.middleware.ZendeskAPIProxyMiddleware.make_zendesk_request")
    @mock.patch("zendesk_api_proxy.middleware.ZendeskAPIProxyMiddleware.make_halo_request")
    def test_halo_request_does_not_call_get_response(
        self,
        make_halo_request: mock.MagicMock,
        make_zendesk_request: mock.MagicMock,
        zendesk_authorization_header: str,
        rf: RequestFactory,
        zendesk_not_required_settings,
        halo_creds_only: HelpDeskCreds,
    ):
        get_response = mock.MagicMock()
        middleware = ZendeskAPIProxyMiddleware(get_response)
        ticket = {
            "subject": "Test ticket subject",
            "description": "Test ticket description",
            "user": "",
        }
        request = rf.post(
            reverse("api:tickets"), data=ticket, HTTP_AUTHORIZATION=zendesk_authorization_header
        )

        middleware(request)

        get_response.assert_not_called()


@mock.patch("zendesk_api_proxy.middleware.ZendeskAPIProxyMiddleware.make_zendesk_request")
class TestUserRequestCache:
    def test_zendesk_data_cached(
        self,
        make_zendesk_request: mock.MagicMock,
        zendesk_authorization_header: str,
        rf: RequestFactory,
        zendesk_required_settings,
        zendesk_creds_only: HelpDeskCreds,
        zendesk_user_create_or_update_request_body,
        zendesk_user_create_or_update_response_body,
    ):
        user_create_or_update_response = HttpResponse(
            json.dumps(zendesk_user_create_or_update_response_body, cls=DjangoJSONEncoder),
            headers={
                "Content-Type": "application/json",
            },
            status=HTTPStatus.OK,
        )
        make_zendesk_request.return_value = user_create_or_update_response
        get_response = mock.MagicMock()
        middleware = ZendeskAPIProxyMiddleware(get_response)
        request = rf.post(
            reverse("api:create_user"),
            data=zendesk_user_create_or_update_request_body,
            content_type="application/json",
            HTTP_AUTHORIZATION=zendesk_authorization_header,
        )

        with mock.patch("zendesk_api_proxy.middleware.caches") as mock_caches:
            mock_cache = MagicMock()
            mock_caches.__getitem__.return_value = mock_cache
            expected_cache_key = zendesk_user_create_or_update_response_body["user"]["id"]
            expected_cache_value = zendesk_user_create_or_update_request_body

            middleware(request)

            mock_caches.__getitem__.assert_called_once_with(settings.USER_DATA_CACHE)
            mock_cache.set.assert_called_once_with(expected_cache_key, expected_cache_value)


class TestHttpMethodsSupported:
    """
    The discovery that Data Workspace uses the Zenpy `ticket.updata()` method
    which in turn uses the HTTP PUT method
    has revealed that we don't have any basic testing of
    how the middleware handles HTTP methods.
    """

    @pytest.mark.parametrize(
        ["url", "http_method"],
        [
            (reverse("api:tickets"), "get"),
            (reverse("api:tickets"), "post"),
            (reverse("api:me"), "get"),
            (reverse("api:user", kwargs={"id": 123}), "get"),
            (reverse("api:user", kwargs={"id": 123}), "post"),
            (reverse("api:create_user"), "post"),
            (reverse("api:ticket", kwargs={"id": 123}), "get"),
            (reverse("api:ticket", kwargs={"id": 123}), "put"),
            (reverse("api:ticket", kwargs={"id": 123}), "post"),
            (reverse("api:comments", kwargs={"id": 123}), "get"),
        ],
    )
    def test_middleware_supports_method_on_halo_view(
        self,
        url,
        http_method,
        zendesk_authorization_header: str,
        halo_creds_only: HelpDeskCreds,
        rf: RequestFactory,
    ):
        request_factory_method = getattr(rf, http_method)
        request = request_factory_method(
            url,
            data={},
            content_type="application/json",
            HTTP_AUTHORIZATION=zendesk_authorization_header,
        )
        mock_get_response = MagicMock()
        middleware = ZendeskAPIProxyMiddleware(mock_get_response)

        with mock.patch(
            "zendesk_api_proxy.middleware.ZendeskAPIProxyMiddleware.cache_request_data"
        ):
            middleware(request)

        mock_get_response.assert_called_once_with(request)
