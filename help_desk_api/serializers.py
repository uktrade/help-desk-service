from copy import deepcopy
from datetime import datetime

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.fields import empty

from help_desk_api.utils.generated_field_mappings import halo_mappings_by_zendesk_id


class ZendeskFieldsNotSupportedException(Exception):
    pass


class ZendeskToHaloCreateCommentSerializer(serializers.Serializer):
    """
    Zendesk Comments Serializer
    """

    ticket_id = serializers.IntegerField()
    outcome = serializers.CharField()
    note = serializers.CharField()

    def validate(self, data):
        # validate
        return data

    def to_representation(self, data):
        zendesk_data = {
            "ticket_id": data["ticket_id"],
            "outcome": "comment",
            "note": data["ticket"]["comment"]["body"],
        }
        return super().to_representation(zendesk_data)


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
                f"The field(s) {unsupported_fields} are not supported in Halo"
            )
        else:
            return super().to_representation(halo_payload)


class ZendeskToHaloCreateUserSerializer(serializers.Serializer):
    """
    Zendesk Payload is converted to Halo Payload
    """

    site_id = serializers.IntegerField(default=1)
    name = serializers.CharField()
    emailaddress = serializers.EmailField()
    other5 = serializers.IntegerField()

    def validate(self, data):
        # validate
        return data

    def to_representation(self, data):
        acceptable_user_fields = set(self.get_fields())
        halo_payload = {"emailaddress": data.pop("email", None), "other5": data.pop("id", None)}
        halo_payload.update(**data)
        unsupported_fields = set(halo_payload.keys()) - acceptable_user_fields

        if unsupported_fields:
            raise ZendeskFieldsNotSupportedException(
                f"The field(s) {unsupported_fields} are not supported in Halo"
            )
        else:
            return super().to_representation(halo_payload)


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
                f"The field(s) {unsupported_fields} are not supported in Halo"
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
                f"The field(s) {unsupported_fields} are not supported in Halo"
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
    email = serializers.EmailField()

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
        zendesk_data = {
            "email": data.get("emailaddress", ""),
            "name": data.get("name", ""),
            "id": data.get("id", ""),
        }
        return super().to_representation(zendesk_data)


class ZendeskCommentToHaloField(serializers.Field):
    serializers = [ZendeskToHaloCreateCommentSerializer]

    def get_attribute(self, instance):
        return instance.get("comment", None)

    def to_representation(self, value):
        return value


class HaloSummaryFromZendeskField(serializers.CharField):
    def get_attribute(self, instance):
        return instance.get("subject", None)


class HaloDetailsFromZendeskField(serializers.CharField):
    def get_attribute(self, instance):
        if "comment" in instance:
            return instance["comment"].get("body", None)
        if "description" in instance:
            return instance["description"]
        return None


class HaloTagsFromZendeskField(serializers.ListField):
    def get_attribute(self, instance):
        return [{"text": tag} for tag in instance.get("tags", [])]


# class Halo


class HaloCustomFieldFromZendeskField(serializers.DictField):
    def halo_name_from_zendesk_id(self, id):
        id = str(id)
        if id not in halo_mappings_by_zendesk_id:
            raise ZendeskFieldsNotSupportedException(
                f"Zendesk field id {id} not found in Halo mappings"
            )
        return halo_mappings_by_zendesk_id[id].halo_title

    def to_representation(self, value):
        return {"name": self.halo_name_from_zendesk_id(value["id"]), "value": value["value"]}


class HaloCustomFieldsSerializer(serializers.ListSerializer):
    child = HaloCustomFieldFromZendeskField()

    def to_representation(self, data):
        return super().to_representation(data)


class HaloUserNameFromZendeskRequesterField(serializers.CharField):
    def get_attribute(self, instance):
        requester = instance.get("requester", {"name": None, "email": None})
        return requester.get("name", None)


class HaloUserEmailFromZendeskRequesterField(serializers.EmailField):
    def get_attribute(self, instance):
        requester = instance.get("requester", {"name": None, "email": None})
        return requester.get("email", None)


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

    site_id = serializers.IntegerField(default=18)
    summary = HaloSummaryFromZendeskField()
    details = HaloDetailsFromZendeskField()
    tags = HaloTagsFromZendeskField(required=False)
    # comment = ZendeskCommentToHaloField()
    customfields = HaloCustomFieldsSerializer(source="custom_fields", required=False)
    user_name = HaloUserNameFromZendeskRequesterField(required=False)
    user_email = HaloUserEmailFromZendeskRequesterField(required=False)

    def validate(self, data):
        return data

    def validate_fields(self, data):
        acceptable_ticket_fields = set(self.get_fields())

        ticket = deepcopy(data)
        halo_payload = {
            "summary": ticket.pop("subject", None),
            "details": ticket.pop("description", None),
            "tags": ticket.pop("tags", []),
        }
        # find unsupported Zendesk fields
        ticket.pop("comment", None)  # Used in comment serializer when updating ticket
        ticket.pop("priority", None)  # Not used by HALO currently
        ticket.pop("recipient", None)  # TODO: add proper support
        ticket.pop("custom_fields", None)  # TODO: add proper support
        ticket.pop("requester", None)  # TODO: add proper support
        halo_payload.update(**ticket)

        unsupported_fields = set(halo_payload.keys()) - acceptable_ticket_fields
        return unsupported_fields

    def to_representation(self, zendesk_ticket_data):
        unsupported_fields = self.validate_fields(zendesk_ticket_data)
        if unsupported_fields:
            raise ZendeskFieldsNotSupportedException(
                f"The field(s) {unsupported_fields} are not supported in Halo"
            )
        # initial_halo_payload = {
        #     "summary": zendesk_ticket_data.get("subject", None),
        #     "details": zendesk_ticket_data.get("description", None),
        #     "tags": [{"text": tag} for tag in zendesk_ticket_data.get("tags", [])],
        # }
        recipient = zendesk_ticket_data.pop("recipient", None)
        serialized_halo_payload = super().to_representation(zendesk_ticket_data)
        if "comment" in serialized_halo_payload:
            comment = serialized_halo_payload.pop("comment")
            if comment:
                attachment_tokens = comment.get("attachments", [])
                if attachment_tokens:
                    serialized_halo_payload["attachments"] = [
                        {"id": attachment_token} for attachment_token in attachment_tokens
                    ]
        if recipient:
            if "customfields" not in serialized_halo_payload:
                serialized_halo_payload["customfields"] = []
            serialized_halo_payload["customfields"].append(
                {"name": "CFEmailToAddress", "value": recipient}
            )
        return serialized_halo_payload


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
                f"The field(s) {unsupported_fields} are not supported in Halo"
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
    custom_fields = ZendeskCustomFieldsFromHaloField()
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
        return super().to_representation(instance)


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
