from copy import deepcopy
from unittest import mock
from unittest.mock import MagicMock

from halo.halo_manager import HaloManager

from help_desk_api import serializers


class TestDFAPIHaloManagerCreateTicket:
    @mock.patch("halo.halo_api_client.HaloAPIClient.post")
    @mock.patch("halo.halo_manager.HaloAPIClient._HaloAPIClient__authenticate")  # /PS-IGNORE
    def test_ticket_creation_api_call_receives_correct_data(
        self,
        mock_halo_authenticate: MagicMock,
        mock_halo_api_client_post: MagicMock,
        client_id,
        client_secret,
        ess_ticket_request_json,
    ):
        mock_halo_authenticate.return_value = "mock-token"
        serializer = serializers.ZendeskToHaloCreateTicketSerializer()
        with mock.patch("help_desk_api.serializers.caches") as mock_caches:
            mock_cache = MagicMock()
            mock_caches.__getitem__.return_value = mock_cache
            mock_cache.get.return_value = {
                "user": {"name": "Some Body", "email": "somebody@example.com"}  # /PS-IGNORE
            }
            expected_request_data = serializer.to_representation(
                deepcopy(ess_ticket_request_json["ticket"])
            )
            expected_path = "Tickets"
            expected_request_kwargs = {
                "path": expected_path,
                "payload": [dict(expected_request_data)],
            }

            halo_manager = HaloManager(client_id=client_id, client_secret=client_secret)
            halo_manager.create_ticket(ess_ticket_request_json)

        mock_halo_api_client_post.assert_called_once_with(**expected_request_kwargs)
