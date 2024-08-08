import markdown

from help_desk_api.serializers import ZendeskToHaloCreateTicketSerializer
from help_desk_api.utils.zendesk_to_halo_service_mappings import service_names_to_ids


class TestDatahubFrontendZendeskToHaloSerialisations:
    def test_subject_is_summary(self, datahub_frontend_support_ticket):
        expected_summary = datahub_frontend_support_ticket["ticket"]["subject"]
        serializer = ZendeskToHaloCreateTicketSerializer(datahub_frontend_support_ticket["ticket"])

        halo_equivalent = serializer.data

        assert "summary" in halo_equivalent
        assert halo_equivalent["summary"] == expected_summary

    def test_comment_is_details(self, datahub_frontend_support_ticket):
        raw_details = datahub_frontend_support_ticket["ticket"]["comment"]["body"]
        expected_details = markdown.markdown(raw_details)
        serializer = ZendeskToHaloCreateTicketSerializer(datahub_frontend_support_ticket["ticket"])

        halo_equivalent = serializer.data

        assert "details_html" in halo_equivalent
        assert halo_equivalent["details_html"] == expected_details

    def test_requester_name_is_user_name(self, datahub_frontend_support_ticket):
        expected_user_name = datahub_frontend_support_ticket["ticket"]["requester"]["name"]
        serializer = ZendeskToHaloCreateTicketSerializer(datahub_frontend_support_ticket["ticket"])

        halo_equivalent = serializer.data

        assert "users_name" in halo_equivalent
        assert halo_equivalent["users_name"] == expected_user_name

    def test_requester_email_is_user_email(self, datahub_frontend_support_ticket):
        expected_user_email = datahub_frontend_support_ticket["ticket"]["requester"]["email"]
        serializer = ZendeskToHaloCreateTicketSerializer(datahub_frontend_support_ticket["ticket"])

        halo_equivalent = serializer.data

        assert "reportedby" in halo_equivalent
        assert halo_equivalent["reportedby"] == expected_user_email

    def test_tags_are_tags(self, datahub_frontend_support_ticket):
        expected_tags = [
            {"text": f"{tag}"} for tag in datahub_frontend_support_ticket["ticket"]["tags"]
        ]
        serializer = ZendeskToHaloCreateTicketSerializer(datahub_frontend_support_ticket["ticket"])

        halo_equivalent = serializer.data

        assert "tags" in halo_equivalent
        assert halo_equivalent["tags"] == expected_tags

    def test_custom_field_service(self, datahub_frontend_support_ticket):
        zendesk_custom_fields = datahub_frontend_support_ticket["ticket"]["custom_fields"]
        zendesk_field = next(
            filter(lambda custom_field: custom_field["id"] == "31281329", zendesk_custom_fields),
            None,
        )
        expected_service_id_in_halo = service_names_to_ids[zendesk_field["value"]]
        serializer = ZendeskToHaloCreateTicketSerializer(datahub_frontend_support_ticket["ticket"])

        halo_equivalent = serializer.data

        assert "customfields" in halo_equivalent
        halo_equivalent = next(
            filter(
                lambda custom_field: custom_field["id"] == 206,  # /PS-IGNORE
                halo_equivalent["customfields"],
            ),
            None,
        )
        assert halo_equivalent is not None
        assert halo_equivalent["value"] == expected_service_id_in_halo

    def test_custom_field_browser(self, datahub_frontend_support_ticket):
        zendesk_custom_fields = datahub_frontend_support_ticket["ticket"]["custom_fields"]
        zendesk_field = next(
            filter(lambda custom_field: custom_field["id"] == "34146805", zendesk_custom_fields),
            None,
        )
        expected_browser = zendesk_field["value"]
        serializer = ZendeskToHaloCreateTicketSerializer(datahub_frontend_support_ticket["ticket"])

        halo_equivalent = serializer.data

        assert "customfields" in halo_equivalent
        halo_equivalent = next(
            filter(
                lambda custom_field: custom_field["id"] == 229,  # /PS-IGNORE
                halo_equivalent["customfields"],
            ),
            None,
        )
        assert halo_equivalent is not None
        assert halo_equivalent["value"] == expected_browser
