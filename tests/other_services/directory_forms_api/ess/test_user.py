from copy import deepcopy
from unittest import mock
from unittest.mock import MagicMock

from django.test import Client
from django.urls import reverse
from halo.halo_manager import HaloManager

from help_desk_api import serializers


class TestDFAPIUserSerialisation:
    def test_user_serialisation_has_email_address(self, ess_user_request_json):
        serialiser = serializers.ZendeskToHaloCreateUserSerializer(ess_user_request_json["user"])

        halo_equivalent = serialiser.data

        assert "emailaddress" in halo_equivalent

    def test_user_serialisation_has_name(self, ess_user_request_json):
        serialiser = serializers.ZendeskToHaloCreateUserSerializer(ess_user_request_json["user"])

        halo_equivalent = serialiser.data

        assert "name" in halo_equivalent


class TestDFAPIHaloManagerCreateUser:
    @mock.patch("halo.halo_api_client.HaloAPIClient.post")
    @mock.patch("halo.halo_manager.HaloAPIClient._HaloAPIClient__authenticate")  # /PS-IGNORE
    def test_user_creation_api_call_receives_correct_data(
        self,
        mock_halo_authenticate: MagicMock,
        mock_halo_api_client_post: MagicMock,
        client_id,
        client_secret,
        ess_user_request_json,
    ):
        mock_halo_authenticate.return_value = "mock-token"
        serializer = serializers.ZendeskToHaloCreateUserSerializer()
        expected_request_data = serializer.to_representation(
            deepcopy(ess_user_request_json["user"])
        )
        expected_path = "Users"
        expected_request_kwargs = {"path": expected_path, "payload": [expected_request_data]}

        halo_manager = HaloManager(client_id=client_id, client_secret=client_secret)
        halo_manager.create_user(ess_user_request_json)

        mock_halo_api_client_post.assert_called_once_with(**expected_request_kwargs)


class TestCreateUserView:
    @mock.patch("halo.halo_manager.HaloManager.create_user")
    @mock.patch("halo.halo_manager.HaloAPIClient._HaloAPIClient__authenticate")  # /PS-IGNORE
    def test_view_unwraps_user_data(
        self,
        mock_halo_authenticate: MagicMock,
        mock_create_user: MagicMock,
        client: Client,
        halo_creds_only,
        zendesk_authorization_header,
        ess_user_request_json,
    ):
        mock_halo_authenticate.return_value = "mock-token"
        mock_create_user.return_value = None
        url = reverse("api:create_user")

        client.post(
            url,
            data=ess_user_request_json,
            content_type="application/json",
            headers={"Authorization": zendesk_authorization_header},
        )

        mock_create_user.assert_called_once_with(ess_user_request_json)
