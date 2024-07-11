from unittest import mock
from unittest.mock import MagicMock

from halo.halo_manager import HaloManager

from help_desk_api.serializers import ZendeskToHaloCreateUserSerializer


@mock.patch("halo.halo_manager.HaloAPIClient._HaloAPIClient__authenticate", return_value="abc123")
@mock.patch("halo.halo_manager.HaloAPIClient.post")
@mock.patch("halo.halo_manager.HaloAPIClient.get")
class TestGetOrCreateUser:
    """
    Directory Forms API uses the Zendesk API's `/v2/users/create_or_update` endpoint.
    On the Halo API, there is no equivalent.
    This tests that posts to that endpoint are correctly handled
    by checking for an existing user in Halo before creating a new one.
    """

    def test_halo_manager_create_user_searches_for_existing_user(
        self,
        mock_get: MagicMock,
        _mock_post: MagicMock,
        _mock_authenticate: MagicMock,
        halo_creds_only,
        halo_user_search_result,
        zendesk_user_create_or_update_request_body,
    ):
        mock_get.return_value = halo_user_search_result
        expected_search_term = zendesk_user_create_or_update_request_body["user"]["email"]
        manager = HaloManager(
            client_id=halo_creds_only.halo_client_id,
            client_secret=halo_creds_only.halo_client_secret,
        )

        manager.create_user(zendesk_user_create_or_update_request_body)

        mock_get.assert_called_once_with(path="Users", params={"search": expected_search_term})

    def test_halo_manager_creates_user_if_no_existing_user(
        self,
        mock_get: MagicMock,
        mock_post: MagicMock,
        _mock_authenticate: MagicMock,
        halo_creds_only,
        halo_user_search_no_results,
        zendesk_user_create_or_update_request_body,
    ):
        mock_get.return_value = halo_user_search_no_results
        zendesk_user = zendesk_user_create_or_update_request_body["user"]
        halo_create_user_serialiser = ZendeskToHaloCreateUserSerializer(zendesk_user)
        halo_create_user_data = halo_create_user_serialiser.data

        manager = HaloManager(
            client_id=halo_creds_only.halo_client_id,
            client_secret=halo_creds_only.halo_client_secret,
        )

        manager.create_user(zendesk_user_create_or_update_request_body)

        mock_post.assert_called_once_with(path="Users", payload=[halo_create_user_data])
