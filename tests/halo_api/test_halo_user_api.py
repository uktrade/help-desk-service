from unittest import mock
from unittest.mock import MagicMock, patch

import pytest
from halo.data_class import ZendeskUser
from halo.halo_api_client import HaloClientNotFoundException
from halo.halo_manager import HaloManager
from tests.fixture_data.halo.user import user as halo_user

from help_desk_api.models import HelpDeskCreds
from help_desk_api.views import UserView


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


class TestUserAPISerializer:
    def test_serialized_user_has_name(self, user_from_manager):
        """ """
        serializer = UserView.serializer_class(user_from_manager)
        response_data = serializer.data

        assert "name" in response_data
        assert response_data["name"] == halo_user["name"]  # /PS-IGNORE

    def test_serialized_user_has_id(self, user_from_manager):
        """
        This will have to be augmented to check the mapping from Halo to Zendesk ID has worked
        """
        serializer = UserView.serializer_class(user_from_manager)
        response_data = serializer.data

        assert "id" in response_data

    def test_serialized_user_has_email(self, user_from_manager):
        """
        Halo uses 'emailaddress', Zendesk uses 'email'
        """
        serializer = UserView.serializer_class(user_from_manager)
        response_data = serializer.data

        assert "email" in response_data
        assert response_data["email"] == halo_user["emailaddress"]  # /PS-IGNORE


class TestUserViews:
    """
    Get User and Create User Tests
    """

    @patch("requests.get")
    @patch("requests.post")
    def test_get_user_success(self, mock_post, mock_get):
        """
        GET User Success
        """
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"access_token": "fake-access-token"}

        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {
            "id": 1,
            "name": "name",
            "email": "test@test.com",  # /PS-IGNORE
        }

        halo_manager = HaloManager(client_id="fake-client-id", client_secret="fake-client-secret")
        user = halo_manager.get_user(1)
        assert isinstance(user, dict)
        assert user["id"] == 1

    @patch("requests.get")
    @patch("requests.post")
    def test_get_user_failure(self, mock_post, mock_get):
        """
        GET User Failure
        """
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {"access_token": "fake-access-token"}

        mock_get.return_value.status_code = 400
        halo_manager = HaloManager(client_id="fake-client-id", client_secret="fake-client-secret")
        with pytest.raises(HaloClientNotFoundException) as excinfo:
            halo_manager.get_user(123)
        assert excinfo.typename == "HaloClientNotFoundException"

    @patch("requests.post")
    def test_post_user_success(self, mock_post):
        """
        POST User Success
        """
        mock_ticket_post = {"id": 123, "name": "dummy name", "email": "test@test.com"}  # /PS-IGNORE
        fake_responses = [mock_post, mock_post]
        fake_responses[0].return_value.json.return_value = {"access_token": "fake-access-token"}
        fake_responses[0].return_value.status_code = 200
        mock_post.side_effects = fake_responses

        halo_manager = HaloManager(client_id="fake-client-id", client_secret="fake-client-secret")
        fake_responses[1].return_value.json.return_value = mock_ticket_post
        fake_responses[1].return_value.status_code = 201
        mock_post.side_effects = fake_responses

        request_data = {"id": 1, "name": "name", "email": "test@email.com"}  # /PS-IGNORE
        user = halo_manager.create_user(request_data)
        assert isinstance(user, ZendeskUser)
        assert user.id == 123

    @patch("requests.post")
    def test_post_user_failure(self, mock_post):
        """
        POST User Failure
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

        request_data = {"id": 123, "name": "name", "email": "test@test.com"}  # /PS-IGNORE
        with pytest.raises(HaloClientNotFoundException) as excinfo:
            halo_manager.create_user(request_data)
        assert excinfo.typename == "HaloClientNotFoundException"

    @patch("requests.post")
    def test_update_user_success(self, mock_post):
        """
        Update User Success
        """
        mock_ticket_post = {"id": 1, "name": "test", "email": "test@test.com"}  # /PS-IGNORE
        fake_responses = [mock_post, mock_post]
        fake_responses[0].return_value.json.return_value = {"access_token": "fake-access-token"}
        fake_responses[0].return_value.status_code = 200
        mock_post.side_effects = fake_responses

        halo_manager = HaloManager(client_id="fake-client-id", client_secret="fake-client-secret")
        fake_responses[1].return_value.json.return_value = mock_ticket_post
        fake_responses[1].return_value.status_code = 201
        mock_post.side_effects = fake_responses

        request_data = {"id": 1, "name": "test"}
        user = halo_manager.create_user(request_data)
        assert isinstance(user, ZendeskUser)
        assert user.name == "test"

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

        request_data = {"id": 1, "name": "test"}
        with pytest.raises(HaloClientNotFoundException) as excinfo:
            halo_manager.update_ticket(request_data)
        assert excinfo.typename == "HaloClientNotFoundException"
