from unittest import mock, skip
from unittest.mock import MagicMock, patch

import pytest
from halo.halo_api_client import (
    HaloClientBadRequestException,
    HaloClientNotFoundException,
)
from halo.halo_manager import HaloManager
from tests.fixture_data.halo.user import user as halo_user

from help_desk_api.models import HelpDeskCreds


@pytest.fixture
@mock.patch("halo.halo_manager.HaloAPIClient._HaloAPIClient__authenticate")  # /PS-IGNORE
def halo_manager(halo_authenticate: MagicMock, halo_creds_only: HelpDeskCreds):
    halo_authenticate.return_value = "mock-token"
    return HaloManager(
        client_id=halo_creds_only.halo_client_id,
        client_secret=halo_creds_only.halo_client_secret,
    )


@pytest.fixture
@mock.patch("halo.halo_manager.HaloAPIClient.get")  # /PS-IGNORE
def user_from_manager(halo_get: MagicMock, halo_manager):
    halo_get.return_value = halo_user
    return halo_manager.get_user(user_id=38)


class TestAgentViews:
    """
    Get Agent and Create Agent Tests
    """

    @patch("requests.get")
    @patch("requests.post")
    def test_get_user_success(self, mock_post, mock_get, access_token):
        """
        GET Agent Success  /PS-IGNORE
        """
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = access_token

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "id": 1,
            "name": "name",
            "email": "test@test.com",  # /PS-IGNORE
            "is_agent": "True",
        }

        halo_manager = HaloManager(client_id="fake-client-id", client_secret="fake-client-secret")
        agent = halo_manager.get_agent(1)
        assert isinstance(agent, dict)
        assert agent["id"] == 1
        assert agent["is_agent"]

    @patch("requests.get")
    @patch("requests.post")
    def test_get_agent_failure(self, mock_post, mock_get, access_token):
        """
        GET Agent Failure  /PS-IGNORE
        """
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = access_token

        mock_get.return_value.status_code = 400
        halo_manager = HaloManager(client_id="fake-client-id", client_secret="fake-client-secret")
        with pytest.raises(HaloClientNotFoundException) as excinfo:
            halo_manager.get_agent(123)
        assert excinfo.typename == "HaloClientNotFoundException"

    @skip("TODO: re-check this stuff before Zendesk to Halo migration")
    @patch("requests.post")
    def test_post_agent_success(self, mock_post, access_token):
        """
        POST Agent Success  /PS-IGNORE
        """
        mock_agent_post = {
            "id": 123,
            "name": "dummy name",
            "email": "test@example.com",  # /PS-IGNORE
        }  # /PS-IGNORE
        fake_responses = [mock_post, mock_post]
        fake_responses[0].return_value.json.return_value = access_token
        fake_responses[0].return_value.status_code = 200
        mock_post.side_effects = fake_responses

        halo_manager = HaloManager(client_id="fake-client-id", client_secret="fake-client-secret")
        fake_responses[1].return_value.json.return_value = mock_agent_post
        fake_responses[1].return_value.status_code = 201
        mock_post.side_effects = fake_responses

        request_data = {
            "site_id": 1,
            "name": "name",
            "email": "test@email.com",  # /PS-IGNORE
            "id": 123,
        }  # /PS-IGNORE
        agent = halo_manager.create_user(request_data)
        assert isinstance(agent, dict)
        assert agent["id"] == 123

    @skip("TODO: re-check this stuff before Zendesk to Halo migration")
    @patch("requests.post")
    def test_post_user_failure(self, mock_post, access_token):
        """
        POST Agent Failure  /PS-IGNORE
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

        request_data = {
            "site_id": 1,
            "name": "name",
            "email": "test@test.com",  # /PS-IGNORE
            "id": 1,
        }  # /PS-IGNORE
        with pytest.raises(HaloClientBadRequestException) as excinfo:
            halo_manager.create_user(request_data)
        assert excinfo.typename == "HaloClientBadRequestException"

    @patch("requests.post")
    def test_update_agent_success(self, mock_post, access_token):
        """
        Update Agent Success  /PS-IGNORE
        """
        mock_agent_post = {
            "id": 1,
            "name": "test",
            "email": "test@test.com",  # /PS-IGNORE
            "default_group_id": 1,
        }  # /PS-IGNORE
        fake_responses = [mock_post, mock_post]
        fake_responses[0].return_value.json.return_value = access_token
        fake_responses[0].return_value.status_code = 200
        mock_post.side_effects = fake_responses

        halo_manager = HaloManager(client_id="fake-client-id", client_secret="fake-client-secret")
        fake_responses[1].return_value.json.return_value = mock_agent_post
        fake_responses[1].return_value.status_code = 201
        mock_post.side_effects = fake_responses

        request_data = {
            "id": 1,
            "name": "x",
            "email": "test@test.com",  # /PS-IGNORE
            "default_group_id": 1,
        }  # /PS-IGNORE
        agent = halo_manager.create_agent(request_data)
        assert isinstance(agent, dict)
        assert agent["name"] == "test"
        assert agent["email"] == "test@test.com"  # /PS-IGNORE
