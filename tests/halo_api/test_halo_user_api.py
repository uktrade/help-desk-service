from unittest import mock
from unittest.mock import MagicMock

import pytest
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
