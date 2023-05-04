from unittest import mock

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
