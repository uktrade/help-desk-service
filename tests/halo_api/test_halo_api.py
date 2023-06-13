import datetime
from unittest.mock import patch

import pytest
from halo.data_class import ZendeskTicket, ZendeskTicketContainer
from halo.halo_api_client import HaloAPIClient, HaloClientNotFoundException
from halo.halo_manager import HaloManager


class TestTicketViews:
    """
    Get Ticket and Create Ticket Tests
    """

    @patch("requests.post")
    def test_token_success(self, mock_post):
        """
        GET Token Success
        """
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"access_token": "fake-access-token"}
        api_client = HaloAPIClient(client_id="fake-id", client_secret="fake-secret")
        assert api_client.access_token == "fake-access-token"

    @patch("requests.post")
    def test_token_failure(self, mock_post):
        """
        GET Token Failure
        """
        mock_post.return_value.status_code = 400
        with pytest.raises(HaloClientNotFoundException) as excinfo:
            HaloAPIClient(client_id="fake-client-id", client_secret="fake-client-secret")
        assert excinfo.typename == "HaloClientNotFoundException"

    @patch("requests.get")
    @patch("requests.post")
    def test_get_ticket_success(self, mock_post, mock_get):
        """
        GET Ticket Success
        """
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"access_token": "fake-access-token"}

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
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
            "customfields": [{"id": 1, "value": 1}],
            "user_email": "test@test.com",  # /PS-IGNORE
            "reportedby": "test",
            "dateoccurred": datetime.datetime.today(),
            "deadlinedate": datetime.datetime.today(),
            "priority": {"name": "low"},
        }

        halo_manager = HaloManager(client_id="fake-client-id", client_secret="fake-client-secret")
        ticket = halo_manager.get_ticket(123)
        assert isinstance(ticket, ZendeskTicketContainer)
        assert isinstance(ticket.ticket, list)
        assert isinstance(ticket.ticket[0], ZendeskTicket)
        assert ticket.ticket[0].subject == "summary"

    @patch("requests.get")
    @patch("requests.post")
    def test_get_ticket_failure(self, mock_post, mock_get):
        """
        GET Ticket Failure
        """
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"access_token": "fake-access-token"}

        mock_get.return_value.status_code = 400
        halo_manager = HaloManager(client_id="fake-client-id", client_secret="fake-client-secret")
        with pytest.raises(HaloClientNotFoundException) as excinfo:
            halo_manager.get_ticket(123)
        assert excinfo.typename == "HaloClientNotFoundException"

    @patch("requests.post")
    def test_post_ticket_success(self, mock_post):
        """
        POST Ticket Success
        """
        mock_ticket_post = {
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
            "customfields": [{"id": 1, "value": 1}],
            "user_email": "test@test.com",  # /PS-IGNORE
            "reportedby": "test",
            "dateoccurred": datetime.datetime.today(),
            "deadlinedate": datetime.datetime.today(),
            "priority": {"name": "low"},
        }
        fake_responses = [mock_post, mock_post]
        fake_responses[0].return_value.json.return_value = {"access_token": "fake-access-token"}
        fake_responses[0].return_value.status_code = 200
        mock_post.side_effects = fake_responses

        halo_manager = HaloManager(client_id="fake-client-id", client_secret="fake-client-secret")
        fake_responses[1].return_value.json.return_value = mock_ticket_post
        fake_responses[1].return_value.status_code = 201
        mock_post.side_effects = fake_responses

        request_data = {
            "ticket": {
                "comment": {"body": "The smoke is very colorful."},
                "priority": "urgent",
                "subject": "My printer is on fire!",
            }
        }
        ticket = halo_manager.create_ticket(request_data)
        assert isinstance(ticket, ZendeskTicketContainer)
        assert isinstance(ticket.ticket, list)
        assert isinstance(ticket.ticket[0], ZendeskTicket)
        assert ticket.ticket[0].subject == "summary"

    @patch("requests.post")
    def test_post_ticket_failure(self, mock_post):
        """
        POST Ticket Failure
        """
        fake_responses = [mock_post, mock_post]
        fake_responses[0].return_value.json.return_value = {"access_token": "fake-access-token"}
        fake_responses[0].return_value.status_code = 200
        mock_post.side_effects = fake_responses

        mock_ticket_post = {}
        halo_manager = HaloManager(client_id="fake-client-id", client_secret="fake-client-secret")
        fake_responses[1].return_value.json.return_value = mock_ticket_post
        fake_responses[1].return_value.status_code = 400
        mock_post.side_effects = fake_responses

        # TODO: add more tests when payload is messed up
        request_data = {"ticket": {"comment": {}}}
        with pytest.raises(HaloClientNotFoundException) as excinfo:
            halo_manager.create_ticket(request_data)
        assert excinfo.typename == "HaloClientNotFoundException"

    @patch("requests.post")
    def test_update_ticket_success(self, mock_post):
        """
        POST Ticket Success
        """
        mock_ticket_post = {
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
            "customfields": [{"id": 1, "value": 1}],
            "user_email": "test@test.com",  # /PS-IGNORE
            "reportedby": "test",
            "dateoccurred": datetime.datetime.today(),
            "deadlinedate": datetime.datetime.today(),
            "priority": {"name": "low"},
        }
        fake_responses = [mock_post, mock_post]
        fake_responses[0].return_value.json.return_value = {"access_token": "fake-access-token"}
        fake_responses[0].return_value.status_code = 200
        mock_post.side_effects = fake_responses

        halo_manager = HaloManager(client_id="fake-client-id", client_secret="fake-client-secret")
        fake_responses[1].return_value.json.return_value = mock_ticket_post
        fake_responses[1].return_value.status_code = 201
        mock_post.side_effects = fake_responses

        request_data = {
            "id": 1,
            "ticket": {
                "comment": {"body": "updated comment"},
            },
        }
        ticket = halo_manager.update_ticket(request_data)
        assert isinstance(ticket, ZendeskTicketContainer)
        assert isinstance(ticket.ticket, list)
        assert isinstance(ticket.ticket[0], ZendeskTicket)
        assert ticket.ticket[0].subject == "summary"

    @patch("requests.post")
    def test_update_ticket_failure(self, mock_post):
        """
        POST Ticket Failure
        """
        fake_responses = [mock_post, mock_post]
        fake_responses[0].return_value.json.return_value = {"access_token": "fake-access-token"}
        fake_responses[0].return_value.status_code = 200
        mock_post.side_effects = fake_responses

        mock_ticket_post = {}
        halo_manager = HaloManager(client_id="fake-client-id", client_secret="fake-client-secret")
        fake_responses[1].return_value.json.return_value = mock_ticket_post
        fake_responses[1].return_value.status_code = 400
        mock_post.side_effects = fake_responses

        # TODO: add more tests when payload is messed up
        request_data = {"id": 1, "ticket": {"comment": {}}}
        with pytest.raises(HaloClientNotFoundException) as excinfo:
            halo_manager.update_ticket(request_data)
        assert excinfo.typename == "HaloClientNotFoundException"
