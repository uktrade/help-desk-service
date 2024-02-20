import pytest

from help_desk_api.serializers import (
    HaloToZendeskTicketContainerSerializer,
    HaloToZendeskTicketSerializer,
    HaloToZendeskUploadSerializer,
    ZendeskPriorityFromHaloField,
    ZendeskStatusFromHaloField,
)


class TestHaloToZendeskTicketSerialisation:
    def test_tags(self, new_halo_ticket):
        expected_tags = {tag["text"] for tag in new_halo_ticket["tags"]}

        zendesk_equivalent = HaloToZendeskTicketSerializer(new_halo_ticket)

        assert "tags" in zendesk_equivalent.data
        assert len(zendesk_equivalent.data["tags"]) == len(new_halo_ticket["tags"])
        for tag in zendesk_equivalent.data["tags"]:
            assert tag in expected_tags

    def test_zendesk_ticket_container_is_not_array(self, new_halo_ticket):
        # Halo Client wraps the ticket data as a Zendesk response
        serializer = HaloToZendeskTicketContainerSerializer(new_halo_ticket)

        zendesk_equivalent = serializer.data

        assert isinstance(zendesk_equivalent, dict)
        assert "ticket" in zendesk_equivalent
        assert isinstance(zendesk_equivalent["ticket"], dict)

    def test_zendesk_ticket_container_includes_audit(self, new_halo_ticket):
        """
        Zendesk ticket updates include an "audit" object alongside the ticket.
        The presence of the audit changes the behaviour of Zenpy,
        so we need to be sure it's present.
        """
        # Halo Client wraps the ticket data as a Zendesk response
        serializer = HaloToZendeskTicketContainerSerializer(new_halo_ticket)

        zendesk_equivalent = serializer.data

        assert isinstance(zendesk_equivalent, dict)
        assert "audit" in zendesk_equivalent
        assert isinstance(zendesk_equivalent["audit"], dict)

    def test_halo_details_is_zendesk_description(self, new_halo_ticket):
        serializer = HaloToZendeskTicketSerializer(new_halo_ticket)
        zendesk_equivalent = serializer.data

        assert "description" in zendesk_equivalent
        assert zendesk_equivalent["description"] == new_halo_ticket["details"]

    def test_halo_summary_is_zendesk_subject(self, new_halo_ticket):
        serializer = HaloToZendeskTicketSerializer(new_halo_ticket)
        zendesk_equivalent = serializer.data

        assert "subject" in zendesk_equivalent
        assert zendesk_equivalent["subject"] == new_halo_ticket["summary"]

    @pytest.mark.parametrize(
        (
            "halo_status_id",
            "expected_zendesk_status",
        ),
        (ZendeskStatusFromHaloField.halo_status_id_to_zendesk_status.items()),
    )
    def test_halo_status_maps_to_zendesk_status(
        self, halo_status_id, expected_zendesk_status, new_halo_ticket
    ):
        new_halo_ticket["status_id"] = halo_status_id
        serializer = HaloToZendeskTicketSerializer(new_halo_ticket)
        zendesk_equivalent = serializer.data

        assert zendesk_equivalent["status"] == expected_zendesk_status

    @pytest.mark.parametrize(
        ("halo_priority_name", "expected_zendesk_priority"),
        ZendeskPriorityFromHaloField.priorities.items(),
    )
    def test_halo_priority_maps_to_zendesk_priority(
        self, expected_zendesk_priority, halo_priority_name, new_halo_ticket
    ):
        new_halo_ticket["priority"]["name"] = halo_priority_name
        serializer = HaloToZendeskTicketSerializer(new_halo_ticket)
        zendesk_equivalent = serializer.data

        assert zendesk_equivalent["priority"] == expected_zendesk_priority

    def test_halo_agent_id_is_zendesk_assignee_id(self, new_halo_ticket):
        serializer = HaloToZendeskTicketSerializer(new_halo_ticket)
        zendesk_equivalent = serializer.data

        assert zendesk_equivalent["assignee_id"] == new_halo_ticket["agent_id"]

    def test_halo_team_id_is_zendesk_group_id(self, new_halo_ticket):
        serializer = HaloToZendeskTicketSerializer(new_halo_ticket)
        zendesk_equivalent = serializer.data

        assert zendesk_equivalent["group_id"] == new_halo_ticket["team_id"]


class TestHaloToZendeskUploadSerializer:
    def test_to_representation(self, halo_upload_response_body):
        serializer = HaloToZendeskUploadSerializer(instance=halo_upload_response_body)

        data = serializer.data

        assert "upload" in data
        assert "token" in data["upload"]
        assert data["upload"]["token"] == halo_upload_response_body["id"]
