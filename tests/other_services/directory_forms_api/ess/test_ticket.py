from copy import deepcopy
from unittest import mock
from unittest.mock import MagicMock

from halo.halo_manager import HaloManager

from help_desk_api import serializers
from help_desk_api.utils.field_mappings import ZendeskToHaloMapping


class TestDFAPITicketSerialisation:
    def test_ticket_serialisation_has_user_id(self, ess_ticket_request_json):
        data = {"requester_id": 1234}
        serializer = serializers.ZendeskToHaloCreateTicketSerializer(data)

        halo_equivalent = serializer.data

        assert "user_id" in halo_equivalent

    def test_custom_field_with_id_and_value(self):
        field_id = "123"
        data = {"id": field_id, "value": "something"}
        expected_value = data["value"]
        expected_title = "expected title"
        serializer = serializers.HaloCustomFieldFromZendeskField()

        with mock.patch.dict(
            "help_desk_api.serializers.halo_mappings_by_zendesk_id",
            {field_id: ZendeskToHaloMapping(halo_title=expected_title)},
            clear=True,
        ):
            halo_equivalent = serializer.to_representation(data)

        assert "value" in halo_equivalent
        assert halo_equivalent["value"] == expected_value
        assert "name" in halo_equivalent
        assert halo_equivalent["name"] == expected_title

    def test_custom_field_with_id_as_key(self):
        """
        Directory Forms API sends some custom fields in this form :-/
        """
        field_id = "123"
        data = {field_id: "something"}
        serializer = serializers.HaloCustomFieldFromZendeskField()
        expected_value = data["123"]
        expected_title = "expected title"

        with mock.patch.dict(
            "help_desk_api.serializers.halo_mappings_by_zendesk_id",
            {field_id: ZendeskToHaloMapping(halo_title=expected_title)},
            clear=True,
        ):
            halo_equivalent = serializer.to_representation(data)

        assert "value" in halo_equivalent
        assert halo_equivalent["value"] == expected_value
        assert "name" in halo_equivalent
        assert halo_equivalent["name"] == expected_title

    def test_custom_field_with_id_as_key_and_list_as_value(self):
        """
        Directory Forms API sends some custom fields in this form :-/
        """
        field_id = "123"
        data = {
            field_id: [
                "something",
                "another",
            ]
        }
        serializer = serializers.HaloCustomFieldFromZendeskField()
        expected_value = data["123"]
        expected_title = "expected title"

        with mock.patch.dict(
            "help_desk_api.serializers.halo_mappings_by_zendesk_id",
            {field_id: ZendeskToHaloMapping(halo_title=expected_title)},
            clear=True,
        ):
            halo_equivalent = serializer.to_representation(data)

        assert "value" in halo_equivalent
        assert halo_equivalent["value"] == expected_value
        assert "name" in halo_equivalent
        assert halo_equivalent["name"] == expected_title


class TestDFAPIHaloManagerCreateTicket:
    @mock.patch("halo.halo_api_client.HaloAPIClient.post")
    @mock.patch("halo.halo_manager.HaloAPIClient._HaloAPIClient__authenticate")  # /PS-IGNORE
    def test_ticket_creation_api_call_receives_correct_data(
        self,
        mock_halo_authenticate: MagicMock,
        mock_halo_api_client_post: MagicMock,
        client_id,
        client_secret,
        ess_ticket_request_json,
    ):
        mock_halo_authenticate.return_value = "mock-token"
        serializer = serializers.ZendeskToHaloCreateTicketSerializer()
        expected_request_data = serializer.to_representation(
            deepcopy(ess_ticket_request_json["ticket"])
        )
        expected_path = "Tickets"
        expected_request_kwargs = {"path": expected_path, "payload": [dict(expected_request_data)]}

        halo_manager = HaloManager(client_id=client_id, client_secret=client_secret)
        halo_manager.create_ticket(ess_ticket_request_json)

        mock_halo_api_client_post.assert_called_once_with(**expected_request_kwargs)
