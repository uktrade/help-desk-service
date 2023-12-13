from unittest import mock

import pytest

from help_desk_api.serializers import (
    HaloCustomFieldFromZendeskField,
    HaloCustomFieldsSerializer,
    HaloDetailsFromZendeskField,
    HaloSummaryFromZendeskField,
    HaloTagsFromZendeskField,
    ZendeskFieldsNotSupportedException,
    ZendeskToHaloCreateTicketSerializer,
)
from help_desk_api.utils.field_mappings import ZendeskToHaloMapping
from help_desk_api.utils.generated_field_mappings import halo_mappings_by_zendesk_id


class TestZendeskToHaloSerialization:
    def test_unknown_zendesk_custom_field(self):
        with mock.patch.dict(
            "help_desk_api.serializers.halo_mappings_by_zendesk_id", {}, clear=True
        ):
            serializer_field = HaloCustomFieldFromZendeskField()
            with pytest.raises(ZendeskFieldsNotSupportedException):
                serializer_field.to_representation({"id": 1, "value": "foo"})

    def test_site_id_in_serialisation(self, zendesk_ticket_subject_and_comment_only):
        serializer = ZendeskToHaloCreateTicketSerializer()

        halo_equivalent = serializer.to_representation(zendesk_ticket_subject_and_comment_only)

        assert "site_id" in halo_equivalent

    def test_zendesk_custom_field_to_halo_custom_field(self, **kwargs):
        with mock.patch.dict(
            "help_desk_api.serializers.halo_mappings_by_zendesk_id",
            {"123": ZendeskToHaloMapping(halo_title="tttttttt")},
            clear=True,
        ):
            serializer_field = HaloCustomFieldFromZendeskField()
            zendesk_field = {"id": 123, "value": "foo"}
            expected_value = zendesk_field["value"]
            expected_title = halo_mappings_by_zendesk_id["123"].halo_title
            halo_equivalent = serializer_field.to_representation(zendesk_field)

        assert "value" in halo_equivalent
        assert halo_equivalent["value"] == expected_value
        assert "name" in halo_equivalent
        assert halo_equivalent["name"] == expected_title

    def test_zendesk_custom_fields_to_halo_custom_fields(self, new_zendesk_ticket_with_description):
        def id_to_name(id):
            return f"name_{id}"

        fixture_custom_field_ids_to_names = {
            str(field["id"]): ZendeskToHaloMapping(halo_title=id_to_name(field["id"]))
            for field in new_zendesk_ticket_with_description["custom_fields"]
        }
        with mock.patch.dict(
            "help_desk_api.serializers.halo_mappings_by_zendesk_id",
            fixture_custom_field_ids_to_names,
            clear=True,
        ):
            serializer = HaloCustomFieldsSerializer(
                new_zendesk_ticket_with_description["custom_fields"]
            )
            halo_equivalent = serializer.data

        for field in serializer.instance:
            field_id_as_name = id_to_name(field["id"])
            halo_custom_field = next(
                filter(lambda halo_field: halo_field["name"] == field_id_as_name, halo_equivalent),
                None,
            )
            assert halo_custom_field is not None
            assert halo_custom_field["value"] == field["value"]

    def test_zendesk_subject_is_halo_summary(self, new_zendesk_ticket_with_description):
        serializer_field = HaloSummaryFromZendeskField()
        halo_equivalent = serializer_field.get_attribute(new_zendesk_ticket_with_description)

        assert halo_equivalent == new_zendesk_ticket_with_description["subject"]

    def test_zendesk_description_is_halo_details(self, new_zendesk_ticket_with_description):
        serializer_field = HaloDetailsFromZendeskField()
        halo_equivalent = serializer_field.get_attribute(new_zendesk_ticket_with_description)

        assert halo_equivalent == new_zendesk_ticket_with_description["description"]

    def test_zendesk_comment_is_halo_details(self, new_zendesk_ticket_with_comment):
        serializer_field = HaloDetailsFromZendeskField()
        halo_equivalent = serializer_field.get_attribute(new_zendesk_ticket_with_comment)

        assert halo_equivalent == new_zendesk_ticket_with_comment["comment"]["body"]

    def test_tags(self, new_zendesk_ticket_with_description):
        serializer_field = HaloTagsFromZendeskField()
        halo_equivalent = serializer_field.get_attribute(new_zendesk_ticket_with_description)

        expected_tags = [tag for tag in new_zendesk_ticket_with_description["tags"]]

        assert len(halo_equivalent) == len(expected_tags)
        for tag in halo_equivalent:
            assert "text" in tag
            assert tag["text"] in expected_tags

    def test_dont_do_rules(self, zendesk_ticket_subject_and_comment_only):
        serializer = ZendeskToHaloCreateTicketSerializer()

        halo_equivalent = serializer.to_representation(zendesk_ticket_subject_and_comment_only)

        assert "dont_do_rules" in halo_equivalent
        assert halo_equivalent["dont_do_rules"] is False


class TestZendeskToHaloTypesMappedFromCSV:
    def test_int_field_is_int(self):
        csv_field = {
            "halo_id": "229",
            "halo_title": "CFBrowser",  # /PS-IGNORE
            "is_zendesk_custom_field": "TRUE",
            "special_treatment": "FALSE",
            "zendesk_id": "34146805",
            "zendesk_title": "Browser",
        }
        field = ZendeskToHaloMapping(**csv_field)
        assert type(field.zendesk_id) is int

    def test_bool_field_is_bool(self):
        csv_field = {
            "halo_id": "229",
            "halo_title": "CFBrowser",  # /PS-IGNORE
            "is_zendesk_custom_field": "TRUE",
            "special_treatment": "FALSE",
            "zendesk_id": "34146805",
            "zendesk_title": "Browser",
        }
        field = ZendeskToHaloMapping(**csv_field)
        assert type(field.is_zendesk_custom_field) is bool

    def test_str_field_is_str(self):
        csv_field = {
            "halo_id": "229",
            "halo_title": "CFBrowser",  # /PS-IGNORE
            "is_zendesk_custom_field": "TRUE",
            "special_treatment": "FALSE",
            "zendesk_id": "34146805",
            "zendesk_title": "Browser",
        }
        field = ZendeskToHaloMapping(**csv_field)
        assert type(field.halo_title) is str
