from halo.zendesk_to_halo import ZendeskToHalo


class TestZendeskToHaloTransformation:
    def test_tags(self, new_zendesk_ticket):
        transformer = ZendeskToHalo()
        expected_tags = {tag for tag in new_zendesk_ticket["ticket"]["tags"]}

        halo_equivalent = transformer.create_ticket_payload(new_zendesk_ticket)

        assert "tags" in halo_equivalent
        assert len(halo_equivalent["tags"]) == len(new_zendesk_ticket["ticket"]["tags"])
        for tag in halo_equivalent["tags"]:
            assert "text" in tag
            assert tag["text"] in expected_tags
