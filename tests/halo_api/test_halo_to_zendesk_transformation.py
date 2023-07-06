from halo.halo_to_zendesk import HaloToZendesk


class TestHaloToZendeskTransformation:
    def test_tags(self, new_halo_ticket):
        transformer = HaloToZendesk()
        expected_tags = {tag["text"] for tag in new_halo_ticket["tags"]}

        zendesk_equivalent = transformer.get_ticket_response_mapping(new_halo_ticket)

        assert "tags" in zendesk_equivalent
        assert len(zendesk_equivalent["tags"]) == len(new_halo_ticket["tags"])
        for tag in zendesk_equivalent["tags"]:
            assert tag in expected_tags
