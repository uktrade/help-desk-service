from unittest.mock import patch

from halo.halo_manager import HaloManager


class TestTicketViews:
    """
    Get Ticket and Create Ticket Tests
    """

    @patch("requests.get")
    @patch("requests.post")
    def test_get_tickets_pagination_success(
        self, mock_post, mock_get, access_token, new_halo_ticket
    ):
        """
        GET Ticket Success
        """
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = access_token

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "pageinate": "true",
            "page_size": 1,
            "page_no": 1,
            "record_count": 2,
            "tickets": [new_halo_ticket],
        }

        halo_manager = HaloManager(client_id="fake-client-id", client_secret="fake-client-secret")
        ticket = halo_manager.get_tickets()
        assert isinstance(ticket, dict)
        assert isinstance(ticket["tickets"], list)
