from copy import deepcopy
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
    ZendeskToHaloCreateUserSerializer,
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

    def test_zendesk_custom_field_to_halo_custom_field(self):
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
        expected_summary = new_zendesk_ticket_with_description["subject"]
        serializer_field = HaloSummaryFromZendeskField()

        halo_equivalent = serializer_field.get_attribute(new_zendesk_ticket_with_description)

        assert halo_equivalent == expected_summary

    def test_zendesk_description_is_halo_details(self, new_zendesk_ticket_with_description):
        expected_details = new_zendesk_ticket_with_description["description"]
        serializer_field = HaloDetailsFromZendeskField()

        halo_equivalent = serializer_field.get_attribute(new_zendesk_ticket_with_description)

        assert halo_equivalent == expected_details

    def test_zendesk_comment_is_halo_details(self, new_zendesk_ticket_with_comment):
        expected_details = new_zendesk_ticket_with_comment["comment"]["body"]
        serializer_field = HaloDetailsFromZendeskField()

        halo_equivalent = serializer_field.get_attribute(new_zendesk_ticket_with_comment)

        assert halo_equivalent == expected_details

    def test_tags(self, new_zendesk_ticket_with_description):
        expected_tags = [tag for tag in new_zendesk_ticket_with_description["tags"]]
        serializer_field = HaloTagsFromZendeskField()

        halo_equivalent = serializer_field.get_attribute(new_zendesk_ticket_with_description)

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


class TestZendeskToHaloServiceCustomFieldsSerialization:
    zendesk_service_to_halo_cfservice = {
        "31281329": ZendeskToHaloMapping(
            halo_title="CFService", special_treatment=True  # /PS-IGNORE
        )
    }
    zendesk_service_name_to_halo_id = {"foo": 9876}

    @mock.patch.dict(
        "help_desk_api.serializers.halo_mappings_by_zendesk_id",
        zendesk_service_to_halo_cfservice,
        clear=True,
    )
    @mock.patch.dict(
        "help_desk_api.serializers.service_names_to_ids",
        zendesk_service_name_to_halo_id,
        clear=True,
    )
    def test_uktrade_service_name_serialized_as_id(self):
        serializer_field = HaloCustomFieldFromZendeskField()
        zendesk_field = {"id": 31281329, "value": "foo"}
        expected_value = self.zendesk_service_name_to_halo_id[zendesk_field["value"]]
        expected_title = self.zendesk_service_to_halo_cfservice["31281329"].halo_title
        halo_equivalent = serializer_field.to_representation(zendesk_field)

        assert "value" in halo_equivalent
        assert halo_equivalent["value"] == expected_value
        assert "name" in halo_equivalent
        assert halo_equivalent["name"] == expected_title


class TestZendeskToHaloUserSerialization:
    def test_serializer_leaves_original_data_intact(self, zendesk_user_get_or_create_response):
        serializer = ZendeskToHaloCreateUserSerializer()
        user_data = zendesk_user_get_or_create_response["user"]
        initial_data_copy = deepcopy(user_data)

        serializer.to_representation(initial_data_copy)

        assert initial_data_copy == user_data
