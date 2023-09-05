from copy import deepcopy

from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers


class ZendeskFieldsNotSupportedException(Exception):
    pass


TICKET_PRIORITIES = (
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
    ("critical", "Critical"),
)


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

        """
        zendesk_data = {
            "emailaddress": data["email"],
            "name": data["name"],
            "other5": data["id"],
            "site_id": data["site_id"],
        }
        return super().to_representation(zendesk_data)
        """


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

    summary = serializers.CharField()
    details = serializers.CharField()
    tags = serializers.ListField()

    def validate(self, data):
        return data

    def validate_fields(self, data):

        acceptable_ticket_fields = set(self.get_fields())

        data_copy = deepcopy(data)
        ticket = data_copy.pop("ticket")
        halo_payload = {
            "summary": ticket.pop("subject", None),
            "details": ticket.pop("description", None),
            "tags": ticket.pop("tags", []),
        }
        # find unsupported Zendesk fields
        ticket.pop("comment", None)  # Used in comment serializer when updating ticket
        ticket.pop("priority", None)  # Not used by HALO currently
        halo_payload.update(**ticket)

        unsupported_fields = set(halo_payload.keys()) - acceptable_ticket_fields
        return unsupported_fields

    def to_representation(self, data):
        zendesk_ticket_data = data.get("ticket", {})
        halo_payload = {
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

        # return super().to_representation(halo_payload)


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


class HaloToZendeskTicketSerializer(serializers.Serializer):
    """
    Zendesk Tickets Serializer
    """

    id = serializers.IntegerField()
    subject = serializers.CharField(max_length=200)
    details = serializers.CharField(max_length=200)
    user = HaloToZendeskUserSerializer()
    group_id = serializers.CharField()
    external_id = serializers.CharField()
    assignee_id = serializers.CharField()
    actions = HaloToZendeskCommentSerializer(many=True)
    tags = serializers.ListField()
    custom_fields = HaloToZendeskCustomFieldsSerializer(many=True)
    recipient_email = serializers.EmailField()
    responder = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    due_at = serializers.DateTimeField()
    # status = serializers.CharField()
    priority = serializers.ChoiceField(
        choices=TICKET_PRIORITIES,
        allow_blank=True,
        default="low",
    )
    assignee_id = serializers.CharField()
    attachments = HaloToZendeskAttachmentSerializer(many=True)

    def validate(self, data):
        return data

    def to_representation(self, data):
        zendesk_response = {
            "id": data["id"],
            "subject": data.get("summary", ""),
            "details": data.get("details", ""),
            "user": data.get("user", {}),
            "group_id": data["id"],
            "external_id": data["id"],
            "assignee_id": data["id"],
            "actions": data.get("actions", []),
            "tags": [tag.get("text", "") for tag in data.get("tags", [])],
            "custom_fields": data.get("customfields", []),
            "recipient_email": data.get("user_email", ""),
            "responder": data.get("reportedby", ""),
            "created_at": data.get("dateoccurred", ""),
            "updated_at": data.get("dateoccurred", ""),
            "due_at": data.get("deadlinedate", ""),
            # "status": data['id'],
            # "priority": data["priority"]["name"],
            "ticket_type": "incident",  # ticket_response['tickettype']['name'],
            "attachments": data.get("attachments", []),
        }
        return super().to_representation(zendesk_response)


class HaloToZendeskTicketContainerSerializer(serializers.Serializer):
    """
    Zendesk Single Ticket Serializer
    """

    ticket = HaloToZendeskTicketSerializer(many=True)


class HaloToZendeskTicketsContainerSerializer(serializers.Serializer):
    """
    Zendesk Multiple Tickets Serializer
    """

    tickets = HaloToZendeskTicketSerializer(many=True)
