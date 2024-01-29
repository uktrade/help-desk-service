from unittest.mock import patch

import pytest
from halo.halo_manager import HaloManager

from help_desk_api.serializers import ZendeskFieldsNotSupportedException


class TestUnsupportedFields:
    """
    POST payload for User and Ticket with Zendesk fields not supported by Halo
    """

    @patch("requests.post")
    def test_update_user_failure(self, mock_post, access_token):
        """
        Unsuccessful User update with unsupported field
        """
        fake_responses = [mock_post, mock_post]
        fake_responses[0].return_value.json.return_value = access_token
        fake_responses[0].return_value.status_code = 200
        mock_post.side_effects = fake_responses

        mock_ticket_post = {}
        halo_manager = HaloManager(client_id="fake-client-id", client_secret="fake-client-secret")
        fake_responses[1].return_value.json.return_value = mock_ticket_post
        fake_responses[1].return_value.status_code = 400
        mock_post.side_effects = fake_responses

        # payload for updating user with unsupported field
        user_data = {
            "name": "name",  # /PS-IGNORE
            "email": "test@example.com",  # /PS-IGNORE
            "id": 1,
            "my_address": "125 Zen Street",
        }
        with pytest.raises(ZendeskFieldsNotSupportedException) as excinfo:
            halo_manager.update_user(user_data)
        assert excinfo.typename == "ZendeskFieldsNotSupportedException"

    @patch("requests.post")
    def test_create_user_failure(self, mock_post, access_token):
        """
        Unsuccessful User create with unsupported field
        """
        fake_responses = [mock_post, mock_post]
        fake_responses[0].return_value.json.return_value = access_token
        fake_responses[0].return_value.status_code = 200
        mock_post.side_effects = fake_responses

        mock_ticket_post = {}
        halo_manager = HaloManager(client_id="fake-client-id", client_secret="fake-client-secret")
        fake_responses[1].return_value.json.return_value = mock_ticket_post
        fake_responses[1].return_value.status_code = 400
        mock_post.side_effects = fake_responses

        # payload for creating user with unsupported field
        user_data = {
            "user": {
                "name": "name",  # /PS-IGNORE
                "email": "test@example.com",  # /PS-IGNORE
                "id": 1,
                "site_id": 1,
                "any_address": "125 Zen Street",
            }
        }
        with pytest.raises(ZendeskFieldsNotSupportedException) as excinfo:
            halo_manager.create_user(user_data)
        assert excinfo.typename == "ZendeskFieldsNotSupportedException"

    @patch("requests.post")
    def test_create_ticket_failure(self, mock_post, access_token):
        """
        Unsuccessful Ticket create with unsupported field
        """
        fake_responses = [mock_post, mock_post]
        fake_responses[0].return_value.json.return_value = access_token
        fake_responses[0].return_value.status_code = 200
        mock_post.side_effects = fake_responses

        mock_ticket_post = {}
        halo_manager = HaloManager(client_id="fake-client-id", client_secret="fake-client-secret")
        fake_responses[1].return_value.json.return_value = mock_ticket_post
        fake_responses[1].return_value.status_code = 400
        mock_post.side_effects = fake_responses

        # payload for creating ticket with unsupported field
        ticket_data = {
            "ticket": {
                "comment": {"body": "The smoke is not very colorful."},
                "priority": "urgent",
                "subject": "My printer is again on fire!",
                "assignee_id": 123,
            }
        }
        with pytest.raises(ZendeskFieldsNotSupportedException) as excinfo:
            halo_manager.create_ticket(ticket_data)
        assert excinfo.typename == "ZendeskFieldsNotSupportedException"

    @patch("requests.post")
    def test_update_ticket_failure(self, mock_post, access_token):
        """
        Unsuccessful Ticket update with unsupported field
        """
        fake_responses = [mock_post, mock_post]
        fake_responses[0].return_value.json.return_value = access_token
        fake_responses[0].return_value.status_code = 200
        mock_post.side_effects = fake_responses

        mock_ticket_post = {}
        halo_manager = HaloManager(client_id="fake-client-id", client_secret="fake-client-secret")
        fake_responses[1].return_value.json.return_value = mock_ticket_post
        fake_responses[1].return_value.status_code = 400
        mock_post.side_effects = fake_responses

        # payload for updating ticket with unsupported field
        ticket_data = {
            "ticket_id": 1,
            "ticket": {
                "comment": {"body": "A comment"},
                "subject": "Asubject",
                "description": "A Description",
                "tags": [],
                "external_id": 2,
                "assignee_id": 3,
            },
        }
        with pytest.raises(ZendeskFieldsNotSupportedException) as excinfo:
            halo_manager.update_ticket(ticket_data)
        assert excinfo.typename == "ZendeskFieldsNotSupportedException"
