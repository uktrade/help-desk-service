from help_desk_api.serializers import (
    HaloToZendeskTicketContainerSerializer,
    HaloToZendeskTicketSerializer,
    HaloToZendeskUploadSerializer,
)


class TestHaloToZendeskTransformation:
    def test_tags(self, new_halo_ticket):
        expected_tags = {tag["text"] for tag in new_halo_ticket["tags"]}

        zendesk_equivalent = HaloToZendeskTicketSerializer(new_halo_ticket)

        assert "tags" in zendesk_equivalent.data
        assert len(zendesk_equivalent.data["tags"]) == len(new_halo_ticket["tags"])
        for tag in zendesk_equivalent.data["tags"]:
            assert tag in expected_tags

    def test_halo_ticket_to_zendesk_ticket(self, new_halo_ticket):
        # Halo Client wraps the ticket data as a Zendesk response
        serializer = HaloToZendeskTicketContainerSerializer(new_halo_ticket)
        serializer.is_valid(raise_exception=False)
        zendesk_equivalent = serializer.data

        assert isinstance(zendesk_equivalent, dict)
        assert "ticket" in zendesk_equivalent
        assert isinstance(zendesk_equivalent["ticket"], dict)


class TestHaloToZendeskUploadSerializer:
    def test_to_representation(self, halo_upload_response_body):
        serializer = HaloToZendeskUploadSerializer(instance=halo_upload_response_body)

        data = serializer.data

        assert "upload" in data
        assert "token" in data["upload"]
        assert data["upload"]["token"] == halo_upload_response_body["id"]
