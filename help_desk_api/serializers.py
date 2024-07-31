from copy import deepcopy
from datetime import datetime

import markdown
from django.conf import settings
from django.core.cache import caches
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.fields import empty

from help_desk_api.utils.generated_field_mappings import halo_mappings_by_zendesk_id
from help_desk_api.utils.utils import apply_zendesk_automatic_html


class ZendeskFieldsNotSupportedException(Exception):
    pass


class ZendeskTicketNoValidUserException(Exception):
    pass


class HaloTicketIDFromZendeskField(serializers.IntegerField):
    def get_attribute(self, instance):
        """
        When we get here, we either have a Zendesk or a Halo ticket ID.
        If it's a Zendesk ID, we need to map it somehow.
        For now, we rely on the cache.
        """
        original_ticket_id = instance.get("id", None)
        cache = caches[settings.TICKET_DATA_CACHE]
        ticket_id = cache.get(original_ticket_id)
        if ticket_id is None:
            # Oh no! Now what will become of us?
            # Something will have to be done, but for now…
            ticket_id = original_ticket_id
        return ticket_id


class HaloNoteFromZendeskField(serializers.CharField):
    def get_attribute(self, instance):
        comment_data = instance.get("comment", {})
        body = comment_data.get("body", comment_data.get("html_body", None))
        body_html = markdown.markdown(body)
        return body_html


class HaloHiddenFromUserFromZendeskField(serializers.BooleanField):
    def get_attribute(self, instance):
        comment_data = instance.get("comment", None)
        if comment_data is None:
            return None
        is_public = comment_data.get("public", False)
        return not is_public


class HaloOutcomeFromZendeskField(serializers.CharField):
    def get_attribute(self, instance):
        comment_data = instance.get("comment", None)
        if comment_data is None:
            return None
        is_public = comment_data.get("public", False)
        return "Public Note" if is_public else self.default


class ZendeskToHaloUpdateCommentSerializer(serializers.Serializer):
    """
    Zendesk Comments Serializer
    """

    ticket_id = serializers.IntegerField()
    id = serializers.IntegerField()
    outcome = serializers.CharField()
    note = serializers.CharField()

    def validate(self, data):
        # validate
        return data

    def to_representation(self, data):
        zendesk_data = {
            "ticket_id": data["ticket_id"],
            "id": data["ticket"]["comment"]["id"],
            "outcome": "comment",
            "note": data["ticket"]["comment"]["body"],
        }
        return super().to_representation(zendesk_data)


class HaloToZendeskCommentSerializer(serializers.Serializer):
    """
    Zendesk Comments Serializer
    """

    id = serializers.IntegerField()
    note = serializers.CharField()
    outcome = serializers.CharField()
    attachments = serializers.ListField(
        child=serializers.IntegerField(), allow_empty=True, default=[]
    )

    def to_representation(self, instance):
        return super().to_representation(instance)


class HaloToZendeskTicketCommentSerializer(serializers.Serializer):
    """
    As Zendesk adds a comment
    by updating the ticket object, we need to be able to respond
    by sending back a `ticket_audit` along with the `ticket`.

    We know Data Workspace does this, but it does nothing
    with the result. So we can send a very minimal response for now.
    """

    def to_representation(self, instance):
        representation = {"audit": {}, "ticket": {"id": instance["ticket_id"]}}
        return representation


class HaloToZendeskCustomFieldsSerializer(serializers.Serializer):
    """
    Zendesk CustomFields Serializer
    """

    id = serializers.IntegerField()
    value = serializers.CharField()


class HaloToZendeskAttachmentSerializer(serializers.Serializer):
    """
    Zendesk Attachments Serializer
    """

    id = serializers.IntegerField()
    filename = serializers.CharField()
    isimage = serializers.BooleanField()


class ZendeskToHaloCreateTeamSerializer(serializers.Serializer):
    """
    Zendesk Group payload is converted to Halo Team payload  /PS-IGNORE
    """

    id = serializers.IntegerField()
    name = serializers.CharField()

    def validate(self, data):
        # validate
        return data

    def to_representation(self, data):
        acceptable_team_fields = set(self.get_fields())
        halo_payload = {"id": data.pop("id", None), "name": data.pop("name", None)}
        halo_payload.update(**data)
        unsupported_fields = set(halo_payload.keys()) - acceptable_team_fields

        if unsupported_fields:
            raise ZendeskFieldsNotSupportedException(
                f"The field(s) {unsupported_fields} aren't supported in Halo"  # noqa: E713
            )
        else:
            return super().to_representation(halo_payload)


class HaloUserNameFromZendeskField(serializers.CharField):
    def get_attribute(self, instance):
        return instance.pop("name", None)


class HaloUserEmailAddressFromZendeskField(serializers.EmailField):
    def get_attribute(self, instance):
        return instance.pop("email", None)


class HaloZendeskUserIdFromZendeskField(serializers.CharField):
    def get_attribute(self, instance):
        value = instance.pop("id", None)
        if value is not None:
            value = str(value)
        return value


class HaloSiteIdField(serializers.IntegerField):
    def get_attribute(self, instance):
        value = super().get_attribute(instance)
        instance.pop("site_id", None)
        return value


class ZendeskToHaloCreateUserSerializer(serializers.Serializer):
    """
    Zendesk Payload is converted to Halo Payload
    """

    site_id = HaloSiteIdField(default=18)  # Needed by Halo. TODO: make default configurable
    name = HaloUserNameFromZendeskField()
    emailaddress = HaloUserEmailAddressFromZendeskField()
    other5 = HaloZendeskUserIdFromZendeskField(required=False)

    def validate(self, data):
        # validate
        return data

    def to_representation(self, data):
        data_copy = deepcopy(data)
        representation = super().to_representation(data_copy)

        unused_field_names = data_copy.keys()
        if unused_field_names:
            raise ZendeskFieldsNotSupportedException(
                f"The field(s) {unused_field_names} are not supported in Halo"  # noqa: E713
            )
        return representation


class ZendeskToHaloCreateAgentSerializer(serializers.Serializer):
    """
    Zendesk Payload is converted to Halo Payload
    """

    name = serializers.CharField()
    email = serializers.EmailField()
    is_agent = serializers.BooleanField(default=True)
    team = serializers.CharField()

    def validate(self, data):
        # validate
        return data

    def to_representation(self, data):
        acceptable_user_fields = set(self.get_fields())
        data.pop("id")
        halo_payload = {"is_agent": True, "team": data.pop("default_group_id", None)}
        halo_payload.update(**data)
        unsupported_fields = set(halo_payload.keys()) - acceptable_user_fields

        if unsupported_fields:
            raise ZendeskFieldsNotSupportedException(
                f"The field(s) {unsupported_fields} are not supported in Halo"  # noqa: E713
            )
        else:
            return super().to_representation(halo_payload)


class ZendeskToHaloUpdateUserSerializer(serializers.Serializer):
    """
    Zendesk Payload is converted to Halo Payload
    """

    id = serializers.IntegerField()
    name = serializers.CharField()
    emailaddress = serializers.EmailField()
    # other5 = serializers.IntegerField()

    def validate(self, data):
        # validate
        return data

    def to_representation(self, data):
        acceptable_user_fields = set(self.get_fields())
        halo_payload = {
            "emailaddress": data.pop("email", None),
        }
        halo_payload.update(**data)

        unsupported_fields = set(halo_payload.keys()) - acceptable_user_fields

        if unsupported_fields:
            raise ZendeskFieldsNotSupportedException(
                f"The field(s) {unsupported_fields} are not supported in Halo"  # noqa: E713
            )
        else:
            return super().to_representation(halo_payload)

        """
        zendesk_data = {
            "emailaddress": data["email"],
            "name": data["name"],
            "other5": data["id"],
            "site_id": data["site_id"],
        }
        return super().to_representation(zendesk_data)
        """


class HaloToZendeskUserSerializer(serializers.Serializer):
    """
    Halo User Serializer (despite the name)

    The only fields that seem to be used within DBT systems are:
    name: str - Full name of the user
    email: str - Email address of the user
    id: int - Zendesk ID of the user

    This will have to map the Halo ID
    to the equivalent Zendesk ID.
    """

    id = serializers.SerializerMethodField(method_name="halo_id_to_zendesk_id")
    name = serializers.CharField()
    email = serializers.EmailField(source="emailaddress")

    @extend_schema_field(
        {
            "type": "string",
        }
    )
    def halo_id_to_zendesk_id(self, instance):
        return instance["id"]  # TODO: mapping to Zendesk ID

    def validate(self, data):
        # validate
        return data

    def to_representation(self, data):
        return super().to_representation(data)


class HaloSummaryFromZendeskField(serializers.CharField):
    def get_attribute(self, instance):
        return instance.pop("subject", None)


class HaloDetailsFromZendeskField(serializers.CharField):
    def get_attribute(self, instance):
        body = None
        if "comment" in instance:
            comment = instance.pop("comment", {})
            body = comment.pop("body", "")
            # Prefer HTML (sent by email router)
            html_body = comment.pop("html_body", "")
            if html_body:
                body = html_body
        if "description" in instance:
            body = instance.pop("description", "")
        # HTML is safe here as it's valid input to a Markdown parser  /PS-IGNORE
        return markdown.markdown(apply_zendesk_automatic_html(body))


class HaloTagsFromZendeskField(serializers.ListField):
    def get_attribute(self, instance):
        return [{"text": tag} for tag in instance.pop("tags", [])]


class HaloCustomFieldFromZendeskField(serializers.DictField):
    specially_excluded_field_values = {"1900000265733": "-", "11013312910749": "-"}

    def halo_mapping_by_zendesk_id(self, field_id):
        field_id = str(field_id)
        mapping = halo_mappings_by_zendesk_id.get(field_id, None)
        if mapping is None:
            raise ZendeskFieldsNotSupportedException(
                f"Zendesk field id {field_id} not found in Halo mappings"  # noqa: E713
            )
        return mapping

    def fix_special_cases(self, field_id, field_value):
        if settings.APP_ENV == "staging":
            from help_desk_api.utils.staging_field_id_mappings import special_cases

            if field_id in special_cases:
                special_case = special_cases[field_id]
                field_id = special_case.replacement_id
                field_value = special_case.replacement_value
        return field_id, field_value

    def to_representation(self, value):
        # D-F-API sends some fields with the ID as the key, so work around that
        if "id" in value:
            field_id = value["id"]
            field_value = value["value"]
        else:
            field_id, field_value = next(iter(value.items()))
        if (
            field_id in self.specially_excluded_field_values
            and field_value == self.specially_excluded_field_values[field_id]
        ):
            return None
        field_id, field_value = self.fix_special_cases(field_id, field_value)
        mapping = self.halo_mapping_by_zendesk_id(field_id)
        try:
            if mapping.value_mappings:
                if mapping.is_multiselect:
                    if not isinstance(field_value, list):
                        field_value = [field_value]
                    field_value = [{"id": mapping.value_mappings[value]} for value in field_value]
                else:
                    field_value = mapping.value_mappings[field_value]
            return {"name": mapping.halo_title, "value": field_value}
        except KeyError as e:
            raise ZendeskFieldsNotSupportedException() from e


class HaloCustomFieldsSerializer(serializers.ListSerializer):
    child = HaloCustomFieldFromZendeskField()

    def to_representation(self, data):
        representation = super().to_representation(data)
        # Tickets from the ESS "emergency" forms have dummy values for certain fields
        # which are stripped out by the child serialiser and come back as None
        # so we need to get them gone
        representation = [datum for datum in representation if datum is not None]
        # data.pop(self.source, [])
        return representation


class HaloUserNameFromZendeskRequesterField(serializers.CharField):
    def get_attribute(self, instance):
        requester = instance.get("requester", {"name": None, "email": None})
        return requester.get("name", None)


class HaloUserEmailFromZendeskRequesterField(serializers.EmailField):
    def get_attribute(self, instance):
        requester = instance.get("requester", {"name": None, "email": None})
        return requester.get("email", None)


class HaloNullIdField(serializers.IntegerField):
    def get_attribute(self, instance):
        id_value = instance.get("id", None)
        if id_value is not None:
            raise ZendeskFieldsNotSupportedException(
                "ID cannot have a non-null value in ticket creation"
            )
        return id_value


class HaloCopyOfZendeskTicketIdField(serializers.CharField):
    def get_attribute(self, instance):
        zendesk_ticket_id = instance.get("zendesk_ticket_id", None)
        return str(zendesk_ticket_id)


class HaloAttachmentFromZendeskUploadField(serializers.IntegerField):
    def to_representation(self, instance):
        # If this was a Zendesk and Halo request,
        # the Halo token should have been cached.
        # If the value isn't in the cache,
        # assume it was Halo-only and use the token as-is.
        cache = caches[settings.UPLOAD_DATA_CACHE]
        halo_token = cache.get(instance, instance)
        return {"id": halo_token}
        # return super().get_attribute(instance)


class HaloAttachmentsFromZendeskUploadsSerializer(serializers.ListField):
    child = HaloAttachmentFromZendeskUploadField()


class ZendeskToHaloCreateTicketSerializer(serializers.Serializer):
    """
    Zendesk to Halo Ticket
    Example Payload:
    {
        "ticket": {
            "comment": {
            "body": "The smoke is very colorful."
            },
            "priority": "urgent",
            "subject": "My printer is on fire!"
        }
    }
    """

    summary = HaloSummaryFromZendeskField()
    details_html = HaloDetailsFromZendeskField()
    tags = HaloTagsFromZendeskField(required=False)
    customfields = HaloCustomFieldsSerializer(source="custom_fields", required=False)
    users_name = HaloUserNameFromZendeskRequesterField(required=False)
    reportedby = HaloUserEmailFromZendeskRequesterField(required=False)
    userdef5 = HaloCopyOfZendeskTicketIdField(required=False)
    attachments = HaloAttachmentsFromZendeskUploadsSerializer(source="uploads", required=False)
    tickettype_id = serializers.IntegerField(default=settings.HALO_DEFAULT_TICKET_TYPE_ID)
    # The dont_do_rules field is a Halo API thing
    # Set it to False to ensure rules are applied
    dont_do_rules = serializers.BooleanField(default=False)
    # Data Workspace will send an id field with a null value
    # so we use this field to consume it
    # without doing anything with it
    # bogus_id = HaloNullIdField(required=False)

    def validate(self, data):
        return data

    def validate_fields(self, data):
        acceptable_ticket_fields = set(self.get_fields())

        ticket = deepcopy(data)
        halo_payload = {
            "summary": ticket.pop("subject", None),
            "details_html": ticket.pop("description", None),
            "tags": ticket.pop("tags", []),
        }
        # find unsupported Zendesk fields
        ticket.pop("comment", None)  # Used in comment serializer when updating ticket
        ticket.pop("priority", None)  # Not used by HALO currently
        ticket.pop("recipient", None)  # TODO: add proper support
        ticket.pop("custom_fields", None)  # TODO: add proper support
        ticket.pop("requester", None)  # TODO: add proper support
        ticket.pop("requester_id", None)  # TODO: add proper support
        ticket.pop("submitter_id", None)  # TODO: add proper support
        ticket.pop("zendesk_ticket_id", None)  # TODO: add proper support
        ticket.pop("id", None)
        halo_payload.update(**ticket)

        unsupported_fields = set(halo_payload.keys()) - acceptable_ticket_fields
        return unsupported_fields

    def to_representation(self, zendesk_ticket_data):
        data_copy = deepcopy(zendesk_ticket_data)
        self.fix_user_fields(data_copy)
        unsupported_fields = self.validate_fields(zendesk_ticket_data)
        if unsupported_fields:
            raise ZendeskFieldsNotSupportedException(
                f"The field(s) {unsupported_fields} aren't supported in Halo"
            )
        # initial_halo_payload = {
        #     "summary": zendesk_ticket_data.get("subject", None),
        #     "details": zendesk_ticket_data.get("description", None),
        #     "tags": [{"text": tag} for tag in zendesk_ticket_data.get("tags", [])],
        # }
        recipient = zendesk_ticket_data.pop("recipient", None)
        # Zendesk includes attachments in comments, Halo in the ticket
        comment = data_copy.get("comment", {})
        upload_tokens = comment.get("uploads", None)
        if upload_tokens:
            data_copy["uploads"] = upload_tokens
        serialized_halo_payload = super().to_representation(data_copy)
        if recipient:
            if "customfields" not in serialized_halo_payload:
                serialized_halo_payload["customfields"] = []
            serialized_halo_payload["customfields"].append(
                {"name": "CFEmailToAddress", "value": recipient}
            )
        return serialized_halo_payload

    def fix_user_fields(self, ticket_data):
        """
        If this comes from D-F-API, the Zendesk user ID in requester_id
        needs to be replaced with the corresponding requester data
        which should have been stashed in the cache by the preceding
        user/create_or_update request
        """
        if "requester" in ticket_data and isinstance(ticket_data["requester"], dict):
            if "name" in ticket_data["requester"] and "email" in ticket_data["requester"]:
                # assume that's already got what we need
                return ticket_data
        if requester_id := ticket_data.get("requester_id", False):
            # This needs to be converted to a requester using info about this user from the cache
            cache = caches[settings.USER_DATA_CACHE]
            if cached_user_data := cache.get(requester_id):
                cached_user = cached_user_data.get("user", {})
                cached_user_name = cached_user.get("name", "")
                cached_user_email = cached_user.get("email", "")
                # Best have a sanity check that the user data is really there
                if not (any([cached_user_name, cached_user_email])):
                    raise ZendeskTicketNoValidUserException(
                        f"Cache for user {requester_id} had neither name nor email"
                    )
                ticket_data["requester"] = {
                    "name": cached_user_name,
                    "email": cached_user_email,
                }
                ticket_data.pop("requester_id")
                return ticket_data
        # At this point, we have no way to identify the user for whom this ticket is being created
        raise ZendeskTicketNoValidUserException("No requester or requester_id found in ticket data")


class ZendeskToHaloUpdateTicketSerializer(serializers.Serializer):
    """
    Zendesk to Halo Ticket
    Example Payload:
    {
        "ticket_id": 123,
        "ticket": {
            "comment": {
            "body": "test"
            },
            "priority": "urgent",
            "subject": "test"
        }
    }
    """

    id = serializers.IntegerField()
    summary = serializers.CharField()
    details = serializers.CharField()
    tags = serializers.ListField()

    def validate(self, data):
        return data

    def validate_fields(self, data):
        # fields defined in this serializer
        acceptable_ticket_fields = set(self.get_fields())

        data_copy = deepcopy(data)
        halo_payload = {
            "id": data_copy.pop("ticket_id", None),
        }
        ticket = data_copy.pop("ticket")
        ticket_payload = {
            "details": ticket.pop("description", None),
            "summary": ticket.pop("subject", None),
            "tags": ticket.pop("tags", []),
        }
        ticket.pop("comment")  # Used in comment serializer so ignore here
        ticket.pop("priority", None)  # Not used by HALO currently
        halo_payload.update(ticket_payload, **ticket)

        unsupported_fields = set(halo_payload.keys()) - acceptable_ticket_fields
        return unsupported_fields

    def to_representation(self, data):
        zendesk_ticket_data = data.get("ticket", {})
        halo_payload = {
            "id": data["ticket_id"],
            "summary": zendesk_ticket_data.get("subject", None),
            "details": zendesk_ticket_data.get("description", None),
            "tags": [{"text": tag} for tag in zendesk_ticket_data.get("tags", [])],
        }

        unsupported_fields = self.validate_fields(data)

        if unsupported_fields:
            raise ZendeskFieldsNotSupportedException(
                f"The field(s) {unsupported_fields} aren't supported in Halo"
            )
        else:
            return super().to_representation(halo_payload)


class ZendeskDescriptionFromHaloField(serializers.CharField):
    def get_attribute(self, instance):
        return instance.get("details", "")


class ZendeskSubjectFromHaloField(serializers.CharField):
    def get_attribute(self, instance):
        return instance.get("summary", "")


class ZendeskTagsFromHaloField(serializers.ListField):
    def get_attribute(self, instance):
        return [tag["text"] for tag in instance.get("tags", [])]


class ZendeskGroupFromHaloField(serializers.IntegerField):
    def get_attribute(self, instance):
        return instance.get("team_id", None)


class ZendeskRecipientFromHaloField(serializers.EmailField):
    def get_attribute(self, instance):
        custom_fields = instance.get("customfields", [])
        recipient_field = next(
            filter(lambda field: field["name"] == "CFEmailToAddress", custom_fields), {}
        )
        return recipient_field.get("value", "")


class ZendeskCreatedAtFromHaloField(serializers.CharField):
    def get_attribute(self, instance):
        return instance.get("dateoccurred", datetime.utcnow().isoformat())


class ZendeskDueAtFromHaloField(serializers.CharField):
    def get_attribute(self, instance):
        return instance.get("fixbydate", datetime.utcnow().isoformat())


class ZendeskUpdatedAtFromHaloField(serializers.CharField):
    def get_attribute(self, instance):
        return instance.get("lastactiondate", datetime.utcnow().isoformat())


class ZendeskCustomFieldFromHaloField(serializers.DictField):
    def get_attribute(self, instance):
        return {"id": instance.get("id", 0), "value": instance.get("value", None)}


class ZendeskCustomFieldsFromHaloField(serializers.ListField):
    child = ZendeskCustomFieldFromHaloField()

    def get_attribute(self, instance):
        return instance.get("customfields", [])


class ZendeskStatusFromHaloField(serializers.CharField):
    halo_status_id_to_zendesk_status = {
        1: "new",
        2: "open",
        4: "pending",
        28: "hold",
        8: "solved",
    }

    def get_attribute(self, instance):
        status_id = instance.get("status_id", "")
        return self.halo_status_id_to_zendesk_status.get(status_id, "")


class ZendeskPriorityFromHaloField(serializers.CharField):
    priorities = {
        "Low": "low",
        "Medium": "medium",
        "High": "high",
        "Critical": "critical",
    }

    def get_attribute(self, instance):
        halo_priority_name = instance.get("priority", {}).get("name", "")
        return self.priorities[halo_priority_name]


class ZendeskAssigneeFromHaloField(serializers.IntegerField):
    def get_attribute(self, instance):
        return instance.get("agent_id", None)


class HaloToZendeskTicketSerializer(serializers.Serializer):
    """
    serilaizer to convert Halo Ticket to Zendesk Ticket  /PS-IGNORE
    """

    id = serializers.IntegerField()
    subject = ZendeskSubjectFromHaloField()
    description = ZendeskDescriptionFromHaloField()
    user = HaloToZendeskUserSerializer()
    group_id = ZendeskGroupFromHaloField()
    # external_id = serializers.CharField() # TODO: fix when getting zenslackchat working
    tags = ZendeskTagsFromHaloField()
    # custom_fields = ZendeskCustomFieldsFromHaloField()  /PS-IGNORE
    recipient = ZendeskRecipientFromHaloField()
    created_at = ZendeskCreatedAtFromHaloField()
    updated_at = ZendeskUpdatedAtFromHaloField()
    due_at = ZendeskDueAtFromHaloField()
    status = ZendeskStatusFromHaloField()
    priority = ZendeskPriorityFromHaloField()
    assignee_id = ZendeskAssigneeFromHaloField()

    def validate(self, data):
        return data


class HaloToZendeskTicketContainerSerializer(serializers.Serializer):
    """
    Zendesk Single Ticket Serializer
    """

    ticket = HaloToZendeskTicketSerializer(many=False)

    def __init__(self, data=empty, **kwargs):
        data = {"ticket": data}
        super().__init__(data, **kwargs)

    def to_representation(self, instance):
        # Zendesk returns an "audit" object alongside the ticket
        # and Zenpy handles things differently if it's present.
        # But our stuff doesn't seem to use it at all,
        # so let's see if just an empty one is enough.
        representation = super().to_representation(instance)
        representation["audit"] = {}
        return representation


class HaloToZendeskTicketsContainerSerializer(serializers.Serializer):
    """
    Zendesk Multiple Tickets Serializer
    """

    tickets = HaloToZendeskTicketSerializer(many=True)


class HaloToZendeskUploadSerializer(serializers.Serializer):
    token = serializers.SerializerMethodField()

    def get_token(self, instance):
        return instance["id"]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {"upload": representation}


class ZendeskToHaloCreateCommentSerializer(serializers.Serializer):
    """
    Zendesk Comments Serializer
    """

    ticket_id = HaloTicketIDFromZendeskField()
    note_html = HaloNoteFromZendeskField()
    hiddenfromuser = HaloHiddenFromUserFromZendeskField()
    outcome = HaloOutcomeFromZendeskField(default="Private Note")
    emailfrom = HaloUserEmailFromZendeskRequesterField(required=False)

    def to_representation(self, data):
        recipient = data.pop("recipient", None)
        representation = super().to_representation(data)
        if recipient:
            if "customfields" not in representation:
                representation["customfields"] = []
            representation["customfields"].append({"name": "CFEmailToAddress", "value": recipient})
        if representation.get("emailfrom", None) is None:
            representation.pop("emailfrom")
        return representation


class ZendeskCommentToHaloField(serializers.Field):
    serializers = [ZendeskToHaloCreateCommentSerializer]

    def get_attribute(self, instance):
        return instance.get("comment", None)

    def to_representation(self, value):
        return value
