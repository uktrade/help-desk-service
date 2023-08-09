from help_desk_api.serializers import ZendeskToHaloCreateTicketSerializer


class TestZendeskToHaloTransformation:
    def test_tags(self, new_zendesk_ticket):
        expected_tags = {tag for tag in new_zendesk_ticket["ticket"]["tags"]}

        halo_equivalent = ZendeskToHaloCreateTicketSerializer(new_zendesk_ticket)
        #print(halo_equivalent.data)
        assert "tags" in halo_equivalent.data
        assert len(halo_equivalent.data["tags"]) == len(new_zendesk_ticket["ticket"]["tags"])
        for tag in halo_equivalent.data["tags"]:
            assert "text" in tag
            assert tag["text"] in expected_tags
