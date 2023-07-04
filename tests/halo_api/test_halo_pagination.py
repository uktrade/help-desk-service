import datetime
from unittest.mock import patch

from halo.data_class import ZendeskTicketsContainer
from halo.halo_manager import HaloManager


class TestTicketViews:
    """
    Get Ticket and Create Ticket Tests
    """

    @patch("requests.get")
    @patch("requests.post")
    def test_get_tickets_pagination_success(self, mock_post, mock_get):
        """
        GET Ticket Success
        """
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"access_token": "fake-access-token"}

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "pageinate": "true",
            "page_size": 1,
            "page_no": 1,
            "record_count": 2,
            "tickets": [
                {
                    "id": 123,
                    "summary": "summary",
                    "details": "details",
                    "user": {"id": 1},
                    "external_id": 1,
                    "assignee_id": 1,
                    "comment": [{"id": 2, "note": "note", "who": "who"}],
                    "tags": [{"id": 1, "text": "test"}],
                    "custom_fields": [{"id": 1, "value": 1}],
                    "recipient_email": "user_email",
                    "responder": "reportedby",
                    "created_at": datetime.datetime.today(),
                    "updated_at": datetime.datetime.today(),
                    "due_at": datetime.datetime.today(),
                    "ticket_type": "incident",
                    "actions": [{"id": 2, "outcome": "comment"}],
                    "attachments": [{"id": 1, "filename": "a", "isimage": True}],
                    "user_id": 1,
                    "customfields": [{"id": 1, "value": "1"}],
                    "user_email": "test@test.com",  # /PS-IGNORE
                    "reportedby": "test",
                    "dateoccurred": datetime.datetime.today(),
                    "deadlinedate": datetime.datetime.today(),
                    "priority": {"name": "low"},
                }
            ],
        }

        halo_manager = HaloManager(client_id="fake-client-id", client_secret="fake-client-secret")
        ticket = halo_manager.get_tickets()
        assert isinstance(ticket, ZendeskTicketsContainer)
        assert isinstance(ticket.tickets, list)
