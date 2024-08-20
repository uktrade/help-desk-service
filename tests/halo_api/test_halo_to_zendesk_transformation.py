from help_desk_api.serializers import (
    HaloToZendeskTicketContainerSerializer,
    HaloToZendeskUploadSerializer,
)


class TestHaloToZendeskTicketSerialisation:
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


class TestHaloToZendeskUploadSerializer:
    def test_to_representation(self, halo_upload_response_body):
        serializer = HaloToZendeskUploadSerializer(instance=halo_upload_response_body)

        data = serializer.data

        assert "upload" in data
        assert "token" in data["upload"]
        assert data["upload"]["token"] == halo_upload_response_body["id"]
