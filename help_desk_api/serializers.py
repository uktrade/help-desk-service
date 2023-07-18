from rest_framework import serializers

TICKET_PRIORITIES = (
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
    ("critical", "Critical"),
)


class ZendeskToHaloCommentSerializer(serializers.Serializer):
    """
    Zendesk Comments Serializer
    """

    ticket_id = serializers.IntegerField()
    # id = serializers.IntegerField()
    outcome = serializers.CharField()
    note = serializers.CharField()

    def validate(self, data):
        # validate
        return data

    def to_representation(self, data):
        zendesk_data = {
            "ticket_id": data["ticket_id"],
            # "id": data.get(
            #     "id",
            # ),
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
    who = serializers.CharField()


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


class ZendeskToHaloUserSerializer(serializers.Serializer):
    """
    Zendesk Payload is converted to Halo Payload
    """

    site_id = serializers.IntegerField(default=1)
    name = serializers.CharField()
    emailaddress = serializers.EmailField()

    def validate(self, data):
        # validate
        return data

    def to_representation(self, data):
        zendesk_data = {
            "emailaddress": data["email"],
            "name": data["name"],
            "site_id": data["site_id"],
        }
        return super().to_representation(zendesk_data)


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

    def halo_id_to_zendesk_id(self, instance):
        return instance["id"]  # TODO: mapping to Zendesk ID

    def validate(self, data):
        # validate
        return data

    def to_representation(self, data):
        zendesk_data = {
            "email": data["emailaddress"],
            "name": data["name"],
            "id": data["id"],
        }
        return super().to_representation(zendesk_data)


class ZendeskToHaloTicketSerializer(serializers.Serializer):
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

    def to_representation(self, data):
        zendesk_ticket_data = data.get("ticket", {})
        halo_payload = {
            "summary": zendesk_ticket_data.get("subject", None),
            "details": zendesk_ticket_data.get("description", None),
            "tags": [{"text": tag} for tag in zendesk_ticket_data.get("tags", [])],
        }
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
    comment = HaloToZendeskCommentSerializer(many=True)
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
            "subject": data.get("subject", ""),
            "details": data.get("details", ""),
            "user": data.get("user", {}),
            "group_id": data["id"],
            "external_id": data["id"],
            "assignee_id": data["id"],
            "comment": data.get("comment", []),
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
