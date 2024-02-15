from copy import deepcopy
from unittest import mock
from unittest.mock import MagicMock

import markdown
import pytest
from django.conf import settings

from help_desk_api.serializers import (
    HaloCustomFieldFromZendeskField,
    HaloCustomFieldsSerializer,
    HaloDetailsFromZendeskField,
    HaloSummaryFromZendeskField,
    HaloTagsFromZendeskField,
    ZendeskFieldsNotSupportedException,
    ZendeskTicketNoValidUserException,
    ZendeskToHaloCreateCommentSerializer,
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
        raw_details = new_zendesk_ticket_with_description["description"]
        expected_details = markdown.markdown(raw_details)
        serializer_field = HaloDetailsFromZendeskField()

        halo_equivalent = serializer_field.get_attribute(new_zendesk_ticket_with_description)

        assert halo_equivalent == expected_details

    def test_zendesk_comment_is_halo_details(self, new_zendesk_ticket_with_comment):
        raw_details = new_zendesk_ticket_with_comment["comment"]["body"]
        expected_details = markdown.markdown(raw_details)
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

    def test_dont_do_rules(self, new_zendesk_ticket_with_comment):
        serializer = ZendeskToHaloCreateTicketSerializer()

        halo_equivalent = serializer.to_representation(new_zendesk_ticket_with_comment)

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
            halo_title="CFService", value_mappings={"foo": 9876}  # /PS-IGNORE
        )
    }

    @mock.patch.dict(
        "help_desk_api.serializers.halo_mappings_by_zendesk_id",
        zendesk_service_to_halo_cfservice,
        clear=True,
    )
    def test_uktrade_service_name_serialized_as_id(self):
        serializer_field = HaloCustomFieldFromZendeskField()
        zendesk_field = {"id": 31281329, "value": "foo"}
        field_mapping = self.zendesk_service_to_halo_cfservice[str(zendesk_field["id"])]
        value_mappings = field_mapping.value_mappings
        expected_value = value_mappings[zendesk_field["value"]]
        expected_title = field_mapping.halo_title
        halo_equivalent = serializer_field.to_representation(zendesk_field)

        assert "value" in halo_equivalent
        assert halo_equivalent["value"] == expected_value
        assert "name" in halo_equivalent
        assert halo_equivalent["name"] == expected_title

    @mock.patch.dict(
        "help_desk_api.serializers.halo_mappings_by_zendesk_id",
        {
            "31281329": ZendeskToHaloMapping(
                halo_title="CFService",  # /PS-IGNORE
                value_mappings={"foo": 9876},
                is_multiselect=True,
            )
        },
        clear=True,
    )
    def test_single_value_for_multiselect_is_list(self):
        serializer_field = HaloCustomFieldFromZendeskField()
        zendesk_field = {"id": 31281329, "value": "foo"}
        field_mapping = self.zendesk_service_to_halo_cfservice[str(zendesk_field["id"])]
        value_mappings = field_mapping.value_mappings
        expected_value = [{"id": value_mappings[zendesk_field["value"]]}]
        halo_equivalent = serializer_field.to_representation(zendesk_field)

        assert "value" in halo_equivalent
        assert halo_equivalent["value"] == expected_value


class TestZendeskToHaloCustomFieldsSerialisation:
    def test_ess_custom_field_serialisation(self, ess_zendesk_ticket_request_body):
        serializer = HaloCustomFieldsSerializer()
        custom_fields = ess_zendesk_ticket_request_body["ticket"]["custom_fields"]

        zendesk_custom_fields_by_ids = {
            custom_field["id"]: custom_field["value"]
            for custom_field in custom_fields
            if "id" in custom_field
        }
        for custom_field in custom_fields:
            if "id" not in custom_field:
                zendesk_custom_fields_by_ids.update(custom_field)

        expected_value_mappings = []
        for id, zendesk_value in zendesk_custom_fields_by_ids.items():
            halo_field_name = halo_mappings_by_zendesk_id[id].halo_title
            halo_mapping = halo_mappings_by_zendesk_id[id]
            halo_value_mappings = halo_mapping.value_mappings
            if halo_value_mappings is None:
                expected_value_mappings.append({"name": halo_field_name, "value": zendesk_value})
                continue
            if halo_mapping.is_multiselect:
                if not isinstance(zendesk_value, list):
                    zendesk_value = [zendesk_value]
                halo_value = [{"id": halo_value_mappings[value]} for value in zendesk_value]
            else:
                halo_value = halo_value_mappings[zendesk_value]
            expected_value_mappings.append({"name": halo_field_name, "value": halo_value})

        halo_equivalent = serializer.to_representation(custom_fields)

        assert halo_equivalent == expected_value_mappings

    def test_data_workspace_staging_special_case_corrected(self, settings):
        special_case_custom_field_id = "44394845"
        special_case_custom_field_value = "data_catalogue"

        expected_special_case_custom_field_id = "31281329"
        expected_special_case_custom_field_value = "data_workspace"

        serializer = HaloCustomFieldFromZendeskField()
        settings.APP_ENV = "staging"

        fixed_id, fixed_value = serializer.fix_special_cases(
            special_case_custom_field_id, special_case_custom_field_value
        )

        assert fixed_id == expected_special_case_custom_field_id
        assert fixed_value == expected_special_case_custom_field_value


class TestZendeskToHaloUserSerialization:
    def test_serializer_leaves_original_data_intact(
        self, zendesk_user_create_or_update_request_body
    ):
        serializer = ZendeskToHaloCreateUserSerializer()
        user_data = zendesk_user_create_or_update_request_body["user"]
        initial_data_copy = deepcopy(user_data)

        serializer.to_representation(initial_data_copy)

        assert initial_data_copy == user_data


class TestZendeskToHaloSerialiserFixUserFields:
    def test_fix_user_fields_leaves_suitable_requester_data_unchanged(
        self, ticket_request_with_suitable_requester
    ):
        serializer = ZendeskToHaloCreateTicketSerializer()

        augmented_zendesk_data = serializer.fix_user_fields(ticket_request_with_suitable_requester)

        assert "requester" in augmented_zendesk_data
        requester_data = augmented_zendesk_data.get("requester", {})
        assert (
            requester_data.get("name", "")
            == ticket_request_with_suitable_requester["requester"]["name"]
        )
        assert (
            requester_data.get("email", "")
            == ticket_request_with_suitable_requester["requester"]["email"]
        )

    def test_fix_user_fields_adds_requester_data_to_unsuitable_request(
        self, ticket_request_with_requester_id
    ):
        serializer = ZendeskToHaloCreateTicketSerializer()

        with mock.patch("help_desk_api.serializers.caches") as mock_caches:
            mock_cache = MagicMock()
            cached_data = {
                "user": {
                    "name": "Some Body",
                    "email": "somebody@example.com",  # /PS-IGNORE
                }
            }
            mock_cache.get.return_value = cached_data
            mock_caches.__getitem__.return_value = mock_cache

            augmented_zendesk_data = serializer.fix_user_fields(ticket_request_with_requester_id)

        assert "requester" in augmented_zendesk_data
        requester_data = augmented_zendesk_data.get("requester", {})
        assert requester_data.get("name", "") == cached_data["user"]["name"]
        assert requester_data.get("email", "") == cached_data["user"]["email"]

    def test_fix_user_fields_raises_for_invalid_cached_user_data(
        self, ticket_request_with_requester_id
    ):
        serializer = ZendeskToHaloCreateTicketSerializer()
        expected_requester_id = ticket_request_with_requester_id["requester_id"]

        with mock.patch("help_desk_api.serializers.caches") as mock_caches:
            mock_cache = MagicMock()
            cached_data = {
                "user": {
                    "name": None,
                    "email": None,
                }
            }
            mock_cache.get.return_value = cached_data
            mock_caches.__getitem__.return_value = mock_cache

            with pytest.raises(ZendeskTicketNoValidUserException) as e:
                serializer.fix_user_fields(ticket_request_with_requester_id)
            assert str(expected_requester_id) in e.value.args[0]

    def test_fix_user_fields_uses_correct_cache(self, ticket_request_with_requester_id):
        serializer = ZendeskToHaloCreateTicketSerializer()
        with mock.patch("help_desk_api.serializers.caches") as mock_caches:
            mock_cache = MagicMock()
            mock_caches.__getitem__.return_value = mock_cache

            serializer.fix_user_fields(ticket_request_with_requester_id)

            mock_caches.__getitem__.assert_called_once_with(settings.USER_DATA_CACHE)

    def test_fix_user_fields_raises_if_no_user_can_be_identified(
        self, ticket_request_lacking_any_requester
    ):
        serializer = ZendeskToHaloCreateTicketSerializer()

        with pytest.raises(ZendeskTicketNoValidUserException):
            serializer.fix_user_fields(ticket_request_lacking_any_requester)


class TestZendeskToHaloSerialiserWithUserCache:
    def test_serializer_uses_suitable_requester_data(self, ticket_request_with_suitable_requester):
        serializer = ZendeskToHaloCreateTicketSerializer()

        halo_equivalent = serializer.to_representation(ticket_request_with_suitable_requester)

        assert (
            halo_equivalent.get("users_name", "")
            == ticket_request_with_suitable_requester["requester"]["name"]
        )
        assert (
            halo_equivalent.get("reportedby", "")
            == ticket_request_with_suitable_requester["requester"]["email"]
        )

    def test_serializer_fixes_unsuitable_requester_data(self, ticket_request_with_requester_id):
        serializer = ZendeskToHaloCreateTicketSerializer()

        with mock.patch("help_desk_api.serializers.caches") as mock_caches:
            mock_cache = MagicMock()
            cached_data = {
                "user": {
                    "name": "Some Body",
                    "email": "somebody@example.com",  # /PS-IGNORE
                }
            }
            mock_cache.get.return_value = cached_data
            mock_caches.__getitem__.return_value = mock_cache

            halo_equivalent = serializer.to_representation(ticket_request_with_requester_id)

        assert halo_equivalent.get("users_name", "") == cached_data["user"]["name"]
        assert halo_equivalent.get("reportedby", "") == cached_data["user"]["email"]

    def test_serializer_raises_for_invalid_cached_user_data(self, ticket_request_with_requester_id):
        serializer = ZendeskToHaloCreateTicketSerializer()
        expected_requester_id = ticket_request_with_requester_id["requester_id"]

        with mock.patch("help_desk_api.serializers.caches") as mock_caches:
            mock_cache = MagicMock()
            cached_data = {
                "user": {
                    "name": None,
                    "email": None,
                }
            }
            mock_cache.get.return_value = cached_data
            mock_caches.__getitem__.return_value = mock_cache

            with pytest.raises(ZendeskTicketNoValidUserException) as e:
                serializer.to_representation(ticket_request_with_requester_id)
            assert str(expected_requester_id) in e.value.args[0]

    def test_serializer_raises_if_no_user_can_be_identified(
        self, ticket_request_lacking_any_requester
    ):
        serializer = ZendeskToHaloCreateTicketSerializer()

        with pytest.raises(ZendeskTicketNoValidUserException):
            serializer.to_representation(ticket_request_lacking_any_requester)


class TestZendeskToHaloTicketCommentSerialization:
    def test_serialized_representation_has_ticket_id(self, private_ticket_comment):
        expected_ticket_id = private_ticket_comment["ticket"]["id"]
        serializer = ZendeskToHaloCreateCommentSerializer()

        halo_equivalent = serializer.to_representation(private_ticket_comment["ticket"])

        assert "ticket_id" in halo_equivalent
        assert halo_equivalent["ticket_id"] == expected_ticket_id

    def test_serialized_representation_has_note(self, private_ticket_comment):
        expected_note = private_ticket_comment["ticket"]["comment"]["body"]
        serializer = ZendeskToHaloCreateCommentSerializer()

        halo_equivalent = serializer.to_representation(private_ticket_comment["ticket"])

        assert "note" in halo_equivalent
        assert halo_equivalent["note"] == expected_note

    def test_serialized_representation_has_hiddenfromuser(self, private_ticket_comment):
        is_public = private_ticket_comment["ticket"]["comment"]["public"]
        expected_hiddenfromuser = not is_public
        serializer = ZendeskToHaloCreateCommentSerializer()

        halo_equivalent = serializer.to_representation(private_ticket_comment["ticket"])

        assert "hiddenfromuser" in halo_equivalent
        assert halo_equivalent["hiddenfromuser"] == expected_hiddenfromuser

    def test_serialized_representation_has_private_outcome(self, private_ticket_comment):
        expected_outcome = "Private Note"
        serializer = ZendeskToHaloCreateCommentSerializer()

        halo_equivalent = serializer.to_representation(private_ticket_comment["ticket"])

        assert "outcome" in halo_equivalent
        assert halo_equivalent["outcome"] == expected_outcome

    def test_serialized_representation_has_public_outcome(self, public_ticket_comment):
        expected_outcome = "Public Note"
        serializer = ZendeskToHaloCreateCommentSerializer()

        halo_equivalent = serializer.to_representation(public_ticket_comment["ticket"])

        assert "outcome" in halo_equivalent
        assert halo_equivalent["outcome"] == expected_outcome
