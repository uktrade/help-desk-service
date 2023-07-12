from rest_framework import serializers

TICKET_PRIORITIES = (
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
    ("critical", "Critical"),
)


class ZendeskUserSerializer(serializers.Serializer):
    """
    Zendesk User Serializer
    """

    id = serializers.IntegerField()
    name = serializers.CharField()
    email = serializers.EmailField()
    site_id = serializers.IntegerField()


class ZendeskCommentSerializer(serializers.Serializer):
    """
    Zendesk Comments Serializer
    """

    id = serializers.IntegerField()
    note = serializers.CharField()
    who = serializers.CharField()


class ZendeskTagSerializer(serializers.Serializer):
    """
    Zendesk Tags Serializer
    """

    id = serializers.IntegerField()
    text = serializers.CharField()


class ZendeskCustomFieldsSerializer(serializers.Serializer):
    """
    Zendesk CustomFields Serializer
    """

    id = serializers.IntegerField()
    value = serializers.CharField()


class ZendeskAttachmentSerializer(serializers.Serializer):
    """
    Zendesk Tags Serializer
    """

    id = serializers.IntegerField()
    filename = serializers.CharField()
    isimage = serializers.BooleanField()


class ZendeskTicketSerializer(serializers.Serializer):
    """
    Zendesk Tickets Serializer
    """

    id = serializers.IntegerField()
    subject = serializers.CharField(max_length=200)
    details = serializers.CharField(max_length=200)
    user = ZendeskUserSerializer()
    group_id = serializers.CharField()
    external_id = serializers.CharField()
    assignee_id = serializers.CharField()
    comment = ZendeskCommentSerializer(many=True)
    tags = serializers.ListField()  # ZendeskTagSerializer(many=True)
    custom_fields = ZendeskCustomFieldsSerializer(many=True)
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
    attachments = ZendeskAttachmentSerializer(many=True)


class ZendeskTicketContainerSerializer(serializers.Serializer):
    """
    Zendesk Single Ticket Serializer
    """

    ticket = ZendeskTicketSerializer(many=True)


class ZendeskTicketsContainerSerializer(serializers.Serializer):
    """
    Zendesk Multiple Tickets Serializer
    """

    tickets = ZendeskTicketSerializer(many=True)


class ZendeskUserSerializer(serializers.Serializer):
    """
    Halo User Serializer (despite the name)

    The only fields that seem to be used within DBT systems are:
    name: str - Full name of the user
    email: str - Email address of the user
    id: int - Zendesk ID of the user

    This will have to map the Halo ID
    to the equivalent Zendesk ID.
    """

    id = serializers.IntegerField()
    name = serializers.CharField()
    email = serializers.EmailField()

    # def halo_id_to_zendesk_id(self, instance):
    #     return instance["id"]  # TODO: mapping to Zendesk ID

    # def to_representation(self, data):
    #     zendesk_data = {
    #         "email": data["emailaddress"],
    #         "name": data["name"],
    #         "id": data["id"],
    #     }
    #     return super().to_representation(zendesk_data)
