import json
from collections import OrderedDict
from unittest import mock
from unittest.mock import MagicMock

from django.http import HttpRequest

from help_desk_api.models import HelpDeskCreds
from help_desk_api.serializers import ZendeskToHaloCreateTicketSerializer
from help_desk_api.views import SingleTicketView, TicketView


class TestDataWorkspaceTicketSerialisation:
    def test_dataset_access_request_initial(self, dataset_access_request_initial):
        serialiser = ZendeskToHaloCreateTicketSerializer()

        halo_equivalent = serialiser.to_representation(dataset_access_request_initial["ticket"])

        assert halo_equivalent is not None


class TestDataWorkspaceUsingHaloApi:
    @mock.patch("halo.halo_manager.HaloManager.add_comment")
    @mock.patch("halo.halo_manager.HaloAPIClient._HaloAPIClient__authenticate")
    def test_comment_put_calls_halo_manager_add_comment(
        self,
        _mock_halo_authenticate: MagicMock,
        mock_halo_add_comment: MagicMock,
        halo_put_ticket_comment_request: HttpRequest,
        ticket_request_kwargs: dict,
    ):
        view = TicketView.as_view()
        mock_halo_add_comment.return_value = {"ticket_id": 1234}

        view(halo_put_ticket_comment_request, **ticket_request_kwargs)

        mock_halo_add_comment.assert_called_once()

    @mock.patch("halo.halo_manager.HaloAPIClient.post")
    @mock.patch("halo.halo_manager.HaloAPIClient._HaloAPIClient__authenticate")
    def test_comment_put_calls_halo_api_post_action(
        self,
        _mock_halo_authenticate: MagicMock,
        mock_halo_post: MagicMock,
        halo_put_ticket_comment_request: HttpRequest,
        ticket_request_kwargs: dict,
    ):
        mock_halo_post.return_value = {"ticket_id": 1234}

        request_content = halo_put_ticket_comment_request.body.decode("utf-8")
        request_data = json.loads(request_content)
        expected_payload = OrderedDict()
        expected_payload["ticket_id"] = request_data["ticket"]["id"]
        expected_payload["note"] = request_data["ticket"]["comment"]["body"]
        expected_payload["hiddenfromuser"] = not request_data["ticket"]["comment"]["public"]
        expected_payload["outcome"] = (
            "Public Note" if request_data["ticket"]["comment"]["public"] else "Private Note"
        )
        view = TicketView.as_view()

        view(halo_put_ticket_comment_request, **ticket_request_kwargs)

        mock_halo_post.assert_called_once_with("Actions", payload=[expected_payload])

    @mock.patch("halo.halo_manager.HaloAPIClient.post")
    @mock.patch("halo.halo_manager.HaloAPIClient._HaloAPIClient__authenticate")
    def test_empty_comment_for_tools_access_fakes_response(
        self,
        _mock_halo_authenticate: MagicMock,
        mock_halo_post: MagicMock,
        halo_creds_only: HelpDeskCreds,
        empty_comment_for_dw_tools_access_request: HttpRequest,
    ):
        view = SingleTicketView.as_view()
        setattr(empty_comment_for_dw_tools_access_request, "help_desk_creds", halo_creds_only)

        response = view(empty_comment_for_dw_tools_access_request, **{"id": 321})

        mock_halo_post.assert_not_called()
        response_json = response.data
        assert "ticket" in response_json
        assert "audit" in response_json
