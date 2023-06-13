from unittest import mock
from unittest.mock import MagicMock

from halo.halo_manager import HaloManager
from tests.fixture_data.halo.user import user as halo_user

from help_desk_api.views import UserView


class TestUserAPI:
    @mock.patch("halo.halo_manager.HaloAPIClient.get")  # /PS-IGNORE
    @mock.patch("halo.halo_manager.HaloAPIClient._HaloAPIClient__authenticate")  # /PS-IGNORE
    def test_get_user(self, halo_authenticate: MagicMock, halo_get: MagicMock, halo_creds_only):
        halo_authenticate.return_value = "mock-token"
        halo_get.return_value = halo_user
        manager = HaloManager(
            client_id=halo_creds_only.halo_client_id,
            client_secret=halo_creds_only.halo_client_secret,
        )

        user = manager.get_user(user_id=38)
        serializer = UserView.serializer_class(user)
        response_data = serializer.data

        assert response_data["full_name"] == "Example User"  # /PS-IGNORE
