from copy import deepcopy
from unittest import mock
from unittest.mock import MagicMock

import markdown
import pytest
from django.conf import settings
from django.core.cache import caches

from help_desk_api.models import CustomField
from help_desk_api.serializers import (
    HaloAttachmentFromZendeskUploadField,
    HaloAttachmentsFromZendeskUploadsSerializer,
    HaloCustomFieldFromZendeskField,
    HaloCustomFieldsSerializer,
    HaloDetailsFromZendeskField,
    HaloSummaryFromZendeskField,
    HaloTagsFromZendeskField,
    HaloTicketIDFromZendeskField,
    ZendeskFieldsNotSupportedException,
    ZendeskTicketNoValidUserException,
    ZendeskToHaloCreateCommentSerializer,
    ZendeskToHaloCreateTicketSerializer,
    ZendeskToHaloCreateUserSerializer,
)


class TestZendeskToHaloSerialization:

    def test_unknown_zendesk_custom_field(self):
        serializer_field = HaloCustomFieldFromZendeskField()
        with pytest.raises(ZendeskFieldsNotSupportedException):
            serializer_field.to_representation({"id": 1, "value": "foo"})

    def test_zendesk_custom_field_to_halo_custom_field(self, service_custom_field):
        zendesk_field_id = service_custom_field["id"]
        custom_field = CustomField.objects.get(zendesk_id=zendesk_field_id)
        zendesk_value = service_custom_field["value"]
        expected_field_id = custom_field.halo_id
        value_mapping = custom_field.values.get(zendesk_value=zendesk_value)
        expected_value_id = value_mapping.halo_id
        serializer_field = HaloCustomFieldFromZendeskField()

        halo_equivalent = serializer_field.to_representation(service_custom_field)

        assert "id" in halo_equivalent
        assert halo_equivalent["id"] == expected_field_id
        assert "value" in halo_equivalent
        assert halo_equivalent["value"] == expected_value_id

    def test_zendesk_custom_fields_to_halo_custom_fields(
        self, minimal_new_zendesk_ticket_with_service_custom_field
    ):
        custom_fields = CustomField.objects.filter(is_multiselect=False).exclude(values=None)
        zendesk_custom_fields = [
            {"id": field.zendesk_id, "value": field.values.last().zendesk_value}
            for field in custom_fields
        ]
        expected_halo_custom_fields = [
            {"id": field.halo_id, "value": field.values.last().halo_id} for field in custom_fields
        ]
        serializer = HaloCustomFieldsSerializer()

        halo_equivalent = serializer.to_representation(zendesk_custom_fields)

        for actual_field, expected_field in zip(halo_equivalent, expected_halo_custom_fields):
            assert actual_field["id"] == expected_field["id"]
            assert actual_field["value"] == expected_field["value"]

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

    def test_dont_do_rules(self, minimal_new_zendesk_ticket):
        serializer = ZendeskToHaloCreateTicketSerializer()

        halo_equivalent = serializer.to_representation(minimal_new_zendesk_ticket)

        assert "dont_do_rules" in halo_equivalent
        assert halo_equivalent["dont_do_rules"] is False


class TestZendeskToHaloServiceCustomFieldsSerialization:
    def test_uktrade_service_name_serialized_as_id(self):
        custom_field = CustomField.objects.get(zendesk_id=31281329)
        custom_field_value = custom_field.values.get(zendesk_value="datahub")
        serializer_field = HaloCustomFieldFromZendeskField()
        zendesk_field = {"id": custom_field.zendesk_id, "value": custom_field_value.zendesk_value}
        expected_field_id = custom_field.halo_id
        expected_value_id = custom_field_value.halo_id

        halo_equivalent = serializer_field.to_representation(zendesk_field)

        assert "id" in halo_equivalent
        assert halo_equivalent["id"] == expected_field_id
        assert "value" in halo_equivalent
        assert halo_equivalent["value"] == expected_value_id

    def test_single_value_for_multiselect_is_list(self):
        custom_field = CustomField.objects.get(zendesk_name="ESS Business type")
        custom_field_value = custom_field.values.first()
        serializer_field = HaloCustomFieldFromZendeskField()
        zendesk_field = {"id": custom_field.zendesk_id, "value": custom_field_value.zendesk_value}
        expected_value = [{"id": custom_field_value.halo_id}]

        halo_equivalent = serializer_field.to_representation(zendesk_field)

        assert "value" in halo_equivalent
        assert halo_equivalent["value"] == expected_value


class TestZendeskToHaloCustomFieldsSerialisation:

    def test_ess_custom_field_serialisation(self, ess_zendesk_ticket_request_body):
        request_custom_fields = ess_zendesk_ticket_request_body["ticket"]["custom_fields"]

        # ESS has a mixture of dicts with {"id": x "value": y} and {x: y}
        # so we need to normalise that
        zendesk_custom_fields_by_ids = {
            custom_field["id"]: custom_field["value"]
            for custom_field in request_custom_fields
            if "id" in custom_field
        }
        for custom_field in request_custom_fields:
            if "id" not in custom_field:
                zendesk_custom_fields_by_ids.update(custom_field)

        custom_fields = CustomField.objects.filter(
            zendesk_id__in=zendesk_custom_fields_by_ids.keys()
        )

        expected_value_mappings = []
        for custom_field in custom_fields:
            request_custom_field_value = zendesk_custom_fields_by_ids.pop(
                str(custom_field.zendesk_id)
            )
            halo_field_id = custom_field.halo_id
            halo_value_id = request_custom_field_value
            if custom_field.is_multiselect:
                if isinstance(request_custom_field_value, str):
                    request_custom_field_value = [
                        request_custom_field_value,
                    ]
                halo_value_id = [
                    {"id": custom_field.values.get(zendesk_value=value).halo_id}
                    for value in request_custom_field_value
                ]
            elif custom_field.values.exists():
                halo_value_id = custom_field.values.get(
                    zendesk_value=request_custom_field_value
                ).halo_id
            halo_value_mapping = {"id": halo_field_id, "value": halo_value_id}
            expected_value_mappings.append(halo_value_mapping)
        serializer = HaloCustomFieldsSerializer()

        halo_equivalent = serializer.to_representation(request_custom_fields)

        def sort_by_id(value):
            return value["id"]

        assert halo_equivalent.sort(key=sort_by_id) == expected_value_mappings.sort(key=sort_by_id)

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
    def test_serialized_representation_has_note(self, private_ticket_comment):
        expected_note = markdown.markdown(private_ticket_comment["ticket"]["comment"]["body"])
        serializer = ZendeskToHaloCreateCommentSerializer()

        halo_equivalent = serializer.to_representation(private_ticket_comment["ticket"])

        assert "note_html" in halo_equivalent
        assert halo_equivalent["note_html"] == expected_note

    def test_serialized_representation_has_html_note(self, comment_via_email_router_reply):
        expected_note = markdown.markdown(
            comment_via_email_router_reply["ticket"]["comment"]["html_body"]
        )
        serializer = ZendeskToHaloCreateCommentSerializer()

        halo_equivalent = serializer.to_representation(comment_via_email_router_reply["ticket"])

        assert "note_html" in halo_equivalent
        assert halo_equivalent["note_html"] == expected_note

    def test_serialized_representation_has_no_emailfrom_field_if_not_relevant(
        self, private_ticket_comment
    ):
        serializer = ZendeskToHaloCreateCommentSerializer()

        halo_equivalent = serializer.to_representation(private_ticket_comment["ticket"])

        assert "emailfrom" not in halo_equivalent

    def test_serialized_representation_has_emailfrom_field_if_relevant(
        self, comment_via_email_router_reply
    ):
        expected_emailfrom = comment_via_email_router_reply["ticket"]["requester"]["email"]
        serializer = ZendeskToHaloCreateCommentSerializer()

        halo_equivalent = serializer.to_representation(comment_via_email_router_reply["ticket"])

        assert "emailfrom" in halo_equivalent
        assert halo_equivalent["emailfrom"] == expected_emailfrom

    def test_comment_via_email_is_visible_to_user(self, comment_via_email_router_reply):
        expected_hiddenfromuser = False
        serializer = ZendeskToHaloCreateCommentSerializer()

        halo_equivalent = serializer.to_representation(comment_via_email_router_reply["ticket"])

        assert "hiddenfromuser" in halo_equivalent
        assert halo_equivalent["hiddenfromuser"] is expected_hiddenfromuser

    def test_comment_via_email_is_public_note(self, comment_via_email_router_reply):
        expected_outcome = "Public Note"
        serializer = ZendeskToHaloCreateCommentSerializer()

        halo_equivalent = serializer.to_representation(comment_via_email_router_reply["ticket"])

        assert "outcome" in halo_equivalent
        assert halo_equivalent["outcome"] == expected_outcome

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

    def test_serialized_representation_has_requester_email(self, public_ticket_comment):
        expected_outcome = "Public Note"
        serializer = ZendeskToHaloCreateCommentSerializer()

        halo_equivalent = serializer.to_representation(public_ticket_comment["ticket"])

        assert "outcome" in halo_equivalent
        assert halo_equivalent["outcome"] == expected_outcome

    def test_ticket_id_field_gets_halo_id_from_cache(
        self, zendesk_add_private_comment_request_body
    ):
        """
        Comment creation gets a Zendesk ticket ID
        which we need to map to the correct Halo ticket ID
        from the ticket ID cache
        """
        zendesk_ticket_id = zendesk_add_private_comment_request_body["ticket"]["id"]
        expected_ticket_id = zendesk_ticket_id + 1
        cache = caches[settings.TICKET_DATA_CACHE]
        cache.set(zendesk_ticket_id, expected_ticket_id)
        field = HaloTicketIDFromZendeskField()

        halo_ticket_id = field.get_attribute(zendesk_add_private_comment_request_body["ticket"])

        assert halo_ticket_id == expected_ticket_id

    def test_serialized_representation_has_halo_ticket_id_from_cache(
        self, zendesk_add_private_comment_request_body
    ):
        zendesk_ticket_id = zendesk_add_private_comment_request_body["ticket"]["id"]
        expected_ticket_id = zendesk_ticket_id + 1
        cache = caches[settings.TICKET_DATA_CACHE]
        cache.set(zendesk_ticket_id, expected_ticket_id)
        serializer = ZendeskToHaloCreateCommentSerializer()

        halo_equivalent = serializer.to_representation(
            zendesk_add_private_comment_request_body["ticket"]
        )

        assert "ticket_id" in halo_equivalent
        assert halo_equivalent["ticket_id"] == expected_ticket_id


class TestHaloTicketTypeIdField:
    def test_ticket_type_id_in_halo_field(self, minimal_new_zendesk_ticket):
        expected_ticket_type_id = settings.HALO_DEFAULT_TICKET_TYPE_ID
        serializer = ZendeskToHaloCreateTicketSerializer()

        halo_equivalent = serializer.to_representation(minimal_new_zendesk_ticket)

        assert "tickettype_id" in halo_equivalent
        assert halo_equivalent["tickettype_id"] == expected_ticket_type_id


class TestUploadSerialization:
    def test_field_uses_zendesk_upload_token_to_fetch_cached_halo_id(self):
        zendesk_upload_token = 1234
        halo_upload_token = 4321
        field = HaloAttachmentFromZendeskUploadField()
        with mock.patch("help_desk_api.serializers.caches") as mock_caches:
            mock_cache = MagicMock()
            mock_caches.__getitem__.return_value = mock_cache
            mock_cache.get.return_value = halo_upload_token

            field.to_representation(zendesk_upload_token)

            mock_caches.__getitem__.assert_called_once_with(settings.UPLOAD_DATA_CACHE)
            mock_cache.get.assert_called_once_with(zendesk_upload_token, zendesk_upload_token)

    def test_field_maps_zendesk_upload_token_to_halo_attachment(self):
        zendesk_upload_token = "1234"
        halo_upload_token = 4321
        expected_halo_value = {"id": halo_upload_token}
        field = HaloAttachmentFromZendeskUploadField()
        with mock.patch("help_desk_api.serializers.caches") as mock_caches:
            mock_cache = MagicMock()
            mock_caches.__getitem__.return_value = mock_cache
            mock_cache.get.return_value = halo_upload_token

            halo_equivalent = field.to_representation(zendesk_upload_token)

            assert halo_equivalent == expected_halo_value

    def test_serialiser_maps_list_of_zendesk_upload_tokens(self):
        zendesk_upload_tokens = ["a", "b", "c"]
        halo_upload_tokens = [
            1,
            2,
            3,
        ]
        expected_halo_attachments = [{"id": id} for id in halo_upload_tokens]
        serializer = HaloAttachmentsFromZendeskUploadsSerializer()
        with mock.patch("help_desk_api.serializers.caches") as mock_caches:
            mock_cache = MagicMock()
            mock_caches.__getitem__.return_value = mock_cache
            mock_cache.get.side_effect = halo_upload_tokens

            halo_equivalent = serializer.to_representation(zendesk_upload_tokens)

            assert halo_equivalent == expected_halo_attachments

    def test_ticket_serialiser_passes_uploads_from_comment(self, new_zendesk_ticket_with_uploads):
        serializer = ZendeskToHaloCreateTicketSerializer()

        halo_equivalent = serializer.to_representation(new_zendesk_ticket_with_uploads["ticket"])

        assert "attachments" in halo_equivalent
