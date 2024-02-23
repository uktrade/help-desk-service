from http import HTTPStatus
from unittest import mock
from unittest.mock import MagicMock

from django.http import HttpResponse
from halo.halo_manager import HaloManager

from help_desk_api.views import HaloBaseView


class TestHaloApiViews:
    def test_base_api_view_has_halo_manager(self, halo_get_tickets_request):
        with mock.patch(
            "halo.halo_manager.HaloAPIClient._HaloAPIClient__authenticate"
        ):  # /PS-IGNORE
            view = HaloBaseView()

            view.initial(halo_get_tickets_request)

        assert hasattr(view, "halo_manager")
        assert view.halo_manager is not None
        assert isinstance(view.halo_manager, HaloManager)

    @mock.patch("help_desk_api.views.TicketView.post")
    @mock.patch("zendesk_api_proxy.middleware.ZendeskAPIProxyMiddleware.make_zendesk_request")
    def test_view_receives_zendesk_ticket_id(
        self,
        mock_make_zendesk_request: MagicMock,
        mock_ticket_view_post: MagicMock,
        zendesk_create_ticket_response: HttpResponse,
    ):
        mock_make_zendesk_request.return_value = zendesk_create_ticket_response
        mock_ticket_view_post.return_value = HttpResponse(b"", status=HTTPStatus.CREATED)
