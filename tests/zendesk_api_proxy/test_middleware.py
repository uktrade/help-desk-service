import json
from http import HTTPStatus
from unittest import mock
from unittest.mock import MagicMock

import pytest
from django.conf import settings
from django.core.cache import caches
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpRequest, HttpResponse
from django.test import Client, RequestFactory
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
        zendesk_create_ticket_response: HttpResponse,
    ):
        make_zendesk_request.return_value = zendesk_create_ticket_response
        get_response = MagicMock()
        middleware = ZendeskAPIProxyMiddleware(get_response)
        ticket = {
            "subject": "Test ticket subject",
            "description": "Test ticket description",
            "user": "",
        }
        request = rf.post(
            reverse("api:tickets"),
            data=ticket,
            content_type="application/json",
            HTTP_AUTHORIZATION=zendesk_authorization_header,
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
        zendesk_create_ticket_response: HttpResponse,
    ):
        make_zendesk_request.return_value = zendesk_create_ticket_response
        get_response = MagicMock()
        middleware = ZendeskAPIProxyMiddleware(get_response)
        ticket = {
            "subject": "Test ticket subject",
            "description": "Test ticket description",
            "user": "",
        }
        request = rf.post(
            reverse("api:tickets"),
            data=ticket,
            content_type="application/json",
            HTTP_AUTHORIZATION=zendesk_authorization_header,
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
        zendesk_create_ticket_response: HttpResponse,
    ):
        make_zendesk_request.return_value = zendesk_create_ticket_response
        get_response = mock.MagicMock()
        middleware = ZendeskAPIProxyMiddleware(get_response)
        ticket = {
            "subject": "Test ticket subject",
            "description": "Test ticket description",
            "user": "",
        }
        request = rf.post(
            reverse("api:tickets"),
            data=ticket,
            content_type="application/json",
            HTTP_AUTHORIZATION=zendesk_authorization_header,
        )

        middleware(request)

        get_response.assert_not_called()


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
        zendesk_create_ticket_response: HttpResponse,
    ):
        make_halo_request.return_value = zendesk_create_ticket_response
        get_response = mock.MagicMock()
        middleware = ZendeskAPIProxyMiddleware(get_response)
        ticket = {
            "subject": "Test ticket subject",
            "description": "Test ticket description",
            "user": "",
        }
        request = rf.post(
            reverse("api:tickets"),
            data=ticket,
            content_type="application/json",
            HTTP_AUTHORIZATION=zendesk_authorization_header,
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
        zendesk_create_ticket_response: HttpResponse,
    ):
        make_halo_request.return_value = zendesk_create_ticket_response
        get_response = mock.MagicMock()
        middleware = ZendeskAPIProxyMiddleware(get_response)
        ticket = {
            "subject": "Test ticket subject",
            "description": "Test ticket description",
            "user": "",
        }
        request = rf.post(
            reverse("api:tickets"),
            data=ticket,
            content_type="application/json",
            HTTP_AUTHORIZATION=zendesk_authorization_header,
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
        zendesk_create_ticket_response: HttpResponse,
    ):
        make_halo_request.return_value = zendesk_create_ticket_response
        get_response = mock.MagicMock()
        middleware = ZendeskAPIProxyMiddleware(get_response)
        ticket = {
            "subject": "Test ticket subject",
            "description": "Test ticket description",
            "user": "",
        }
        request = rf.post(
            reverse("api:tickets"),
            data=ticket,
            content_type="application/json",
            HTTP_AUTHORIZATION=zendesk_authorization_header,
        )

        middleware(request)

        get_response.assert_not_called()


@mock.patch("zendesk_api_proxy.middleware.ZendeskAPIProxyMiddleware.make_zendesk_request")
class TestZendeskRequestCache:
    def test_zendesk_user_data_cached(
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

    @mock.patch("zendesk_api_proxy.middleware.ZendeskAPIProxyMiddleware.make_halo_request")
    def test_halo_ticket_id_cached_under_zendesk_id(
        self,
        make_halo_request: mock.MagicMock,
        make_zendesk_request: mock.MagicMock,
        zendesk_authorization_header: str,
        zendesk_required_settings,
        zendesk_and_halo_creds: HelpDeskCreds,
        zendesk_create_ticket_request: HttpRequest,
        zendesk_create_ticket_response: HttpResponse,
    ):
        make_zendesk_request.return_value = zendesk_create_ticket_response
        make_halo_request.return_value = zendesk_create_ticket_response
        get_response = mock.MagicMock()
        middleware = ZendeskAPIProxyMiddleware(get_response)

        with mock.patch("zendesk_api_proxy.middleware.caches") as mock_caches:
            mock_cache = MagicMock()
            mock_caches.__getitem__.return_value = mock_cache
            response_content = zendesk_create_ticket_response.content.decode("utf-8")
            response_json = json.loads(response_content)
            expected_cache_key = response_json["ticket"]["id"]
            expected_cache_value = expected_cache_key

            middleware(zendesk_create_ticket_request)

            mock_caches.__getitem__.assert_called_once_with(settings.TICKET_DATA_CACHE)
            mock_cache.set.assert_called_once_with(expected_cache_key, expected_cache_value)

    @mock.patch("zendesk_api_proxy.middleware.ZendeskAPIProxyMiddleware.make_halo_request")
    def test_halo_ticket_id_really_is_cached_under_zendesk_id(
        self,
        make_halo_request: mock.MagicMock,
        make_zendesk_request: mock.MagicMock,
        zendesk_authorization_header: str,
        zendesk_required_settings,
        zendesk_and_halo_creds: HelpDeskCreds,
        zendesk_create_ticket_request: HttpRequest,
        zendesk_create_ticket_response: HttpResponse,
        halo_create_ticket_response: HttpResponse,
    ):
        """
        SO…
        Create ticket, with different ticket IDs in the responses
        Add comment to ticket, using the Zendesk ticket ID
        Check that Halo comment-adding request has Halo ticket ID
        """
        make_zendesk_request.return_value = zendesk_create_ticket_response
        make_halo_request.return_value = halo_create_ticket_response
        get_response = mock.MagicMock()
        middleware = ZendeskAPIProxyMiddleware(get_response)
        zendesk_response_content = zendesk_create_ticket_response.content.decode("utf-8")
        zendesk_response_json = json.loads(zendesk_response_content)
        expected_cache_key = zendesk_response_json["ticket"]["id"]
        halo_response_content = halo_create_ticket_response.content.decode("utf-8")
        halo_response_json = json.loads(halo_response_content)
        expected_cache_value = halo_response_json["ticket"]["id"]

        middleware(zendesk_create_ticket_request)

        cache = caches[settings.TICKET_DATA_CACHE]
        cached_halo_id = cache.get(expected_cache_key)
        assert cached_halo_id == expected_cache_value

    @mock.patch("zendesk_api_proxy.middleware.ZendeskAPIProxyMiddleware.make_halo_request")
    def test_halo_upload_id_cached_under_zendesk_id(
        self,
        make_halo_request: mock.MagicMock,
        make_zendesk_request: mock.MagicMock,
        zendesk_authorization_header: str,
        zendesk_required_settings,
        zendesk_and_halo_creds: HelpDeskCreds,
        zendesk_upload_request: HttpRequest,
        zendesk_upload_response: HttpResponse,
        halo_upload_response: HttpResponse,
    ):
        make_zendesk_request.return_value = zendesk_upload_response
        make_halo_request.return_value = halo_upload_response
        get_response = mock.MagicMock()
        middleware = ZendeskAPIProxyMiddleware(get_response)

        with mock.patch("zendesk_api_proxy.middleware.caches") as mock_caches:
            mock_cache = MagicMock()
            mock_caches.__getitem__.return_value = mock_cache
            zendesk_response_content = zendesk_upload_response.content.decode("utf-8")
            zendesk_response_json = json.loads(zendesk_response_content)
            expected_cache_key = zendesk_response_json["upload"]["token"]
            halo_response_content = halo_upload_response.content.decode("utf-8")
            halo_response_json = json.loads(halo_response_content)
            expected_cache_value = halo_response_json["upload"]["token"]

            middleware(zendesk_upload_request)

            mock_caches.__getitem__.assert_called_once_with(settings.UPLOAD_DATA_CACHE)
            mock_cache.set.assert_called_once_with(expected_cache_key, expected_cache_value)


class TestHttpMethodsSupported:
    """
    The discovery that Data Workspace uses the Zenpy `ticket.update()` method
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


class TestZendeskResponseIDsPersisted:
    @mock.patch("zendesk_api_proxy.middleware.ZendeskAPIProxyMiddleware.make_zendesk_request")
    @mock.patch("zendesk_api_proxy.middleware.ZendeskAPIProxyMiddleware.make_halo_request")
    def test_zendesk_ticket_response_id_passed_to_halo_request(
        self,
        mock_make_halo_request: MagicMock,
        mock_make_zendesk_request: MagicMock,
        zendesk_create_ticket_request,
        zendesk_create_ticket_response: HttpResponse,
        zendesk_and_halo_creds,
    ):
        mock_make_zendesk_request.return_value = zendesk_create_ticket_response
        mock_make_halo_request.return_value = zendesk_create_ticket_response
        mock_get_response = MagicMock()
        middleware = ZendeskAPIProxyMiddleware(mock_get_response)

        middleware(zendesk_create_ticket_request)

        mock_make_halo_request.assert_called_once_with(
            zendesk_and_halo_creds, zendesk_create_ticket_request, True
        )

    @mock.patch("zendesk_api_proxy.middleware.ZendeskAPIProxyMiddleware.make_zendesk_request")
    @mock.patch("zendesk_api_proxy.middleware.ZendeskAPIProxyMiddleware.make_halo_request")
    def test_create_ticket_request_has_zendesk_id(
        self,
        mock_make_halo_request: MagicMock,
        mock_make_zendesk_request: MagicMock,
        zendesk_create_ticket_request: HttpRequest,
        zendesk_create_ticket_response: HttpResponse,
        zendesk_and_halo_creds,
    ):
        raw_zendesk_response_data = zendesk_create_ticket_response.content.decode("utf-8")
        zendesk_response_data = json.loads(raw_zendesk_response_data)
        expected_zendesk_ticket_id = zendesk_response_data["ticket"]["id"]

        mock_make_zendesk_request.return_value = zendesk_create_ticket_response
        mock_make_halo_request.return_value = zendesk_create_ticket_response
        mock_get_response = MagicMock()
        middleware = ZendeskAPIProxyMiddleware(mock_get_response)

        middleware(zendesk_create_ticket_request)

        actual_request_used = mock_make_halo_request.call_args.args[1]
        assert hasattr(actual_request_used, "zendesk_ticket_id")
        assert getattr(actual_request_used, "zendesk_ticket_id") == expected_zendesk_ticket_id

    @mock.patch("zendesk_api_proxy.middleware.ZendeskAPIProxyMiddleware.make_zendesk_request")
    @mock.patch("help_desk_api.views.HaloManager.create_ticket")
    @mock.patch("halo.halo_manager.HaloAPIClient._HaloAPIClient__authenticate")
    def test_halo_manager_create_ticket_request_has_zendesk_id(
        self,
        mock_halo_authenticate,
        mock_halo_manager_create_ticket: MagicMock,
        mock_make_zendesk_request: MagicMock,
        new_zendesk_ticket_with_comment: dict,
        zendesk_create_ticket_response: HttpResponse,
        zendesk_and_halo_creds,
        zendesk_authorization_header,
        new_halo_ticket,
        client: Client,
    ):
        mock_halo_authenticate.return_value = "mock-token"
        raw_zendesk_response_data = zendesk_create_ticket_response.content.decode("utf-8")
        zendesk_response_data = json.loads(raw_zendesk_response_data)
        expected_zendesk_ticket_id = zendesk_response_data["ticket"]["id"]
        mock_halo_manager_create_ticket.return_value = new_halo_ticket
        mock_make_zendesk_request.return_value = zendesk_create_ticket_response
        url = reverse("api:tickets")

        client.post(
            url,
            data=new_zendesk_ticket_with_comment,
            content_type="application/json",
            headers={"Authorization": zendesk_authorization_header},
        )

        mock_halo_manager_create_ticket.assert_called_once()
        zendesk_data_passed_to_halo_manager = mock_halo_manager_create_ticket.call_args.args[0]
        assert "zendesk_ticket_id" in zendesk_data_passed_to_halo_manager
        assert (
            zendesk_data_passed_to_halo_manager["zendesk_ticket_id"] == expected_zendesk_ticket_id
        )

    @mock.patch("help_desk_api.views.HaloManager.create_ticket")
    @mock.patch("halo.halo_manager.HaloAPIClient._HaloAPIClient__authenticate")
    def test_halo_only_ticket_creation_passes_null_zendesk_ticket_id(
        self,
        mock_halo_authenticate,
        mock_halo_manager_create_ticket: MagicMock,
        new_zendesk_ticket_with_comment: dict,
        halo_creds_only,
        zendesk_authorization_header,
        new_halo_ticket,
        client: Client,
    ):
        mock_halo_authenticate.return_value = "mock-token"
        mock_halo_manager_create_ticket.return_value = new_halo_ticket
        url = reverse("api:tickets")

        client.post(
            url,
            data=new_zendesk_ticket_with_comment,
            content_type="application/json",
            headers={"Authorization": zendesk_authorization_header},
        )

        mock_halo_manager_create_ticket.assert_called_once()
        zendesk_data_passed_to_halo_manager = mock_halo_manager_create_ticket.call_args.args[0]
        assert "zendesk_ticket_id" in zendesk_data_passed_to_halo_manager
        assert zendesk_data_passed_to_halo_manager["zendesk_ticket_id"] is None
