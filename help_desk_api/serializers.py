from rest_framework import serializers

TICKET_PRIORITIES = (
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
    ("critical", "Critical"),
)


class ZendeskUserSerializer(serializers.Serializer):
    """
    Halo User Serializer
    """

    id = serializers.IntegerField()
    name = serializers.CharField()
    emailaddress = serializers.EmailField()
    site_id = serializers.IntegerField()


class ZendeskCommentSerializer(serializers.Serializer):
    """
    Comments Serializer
    """

    id = serializers.IntegerField()
    note = serializers.CharField()
    who = serializers.CharField()


class ZendeskTagSerializer(serializers.Serializer):
    """
    Tags Serializer
    """

    id = serializers.IntegerField()
    text = serializers.CharField()


class ZendeskCustomFieldsSerializer(serializers.Serializer):
    """
    CustomFields Serializer
    """

    id = serializers.IntegerField()
    value = serializers.CharField()


class ZendeskAttachmentSerializer(serializers.Serializer):
    """
    Tags Serializer
    """

    id = serializers.IntegerField()
    filename = serializers.CharField()
    isimage = serializers.BooleanField()


class ZendeskTicketSerializer(serializers.Serializer):
    """
    Tickets Serializer
    """

    id = serializers.IntegerField()
    subject = serializers.CharField(max_length=200)
    details = serializers.CharField(max_length=200)
    user = ZendeskUserSerializer(many=True)
    group_id = serializers.CharField()
    external_id = serializers.CharField()
    assignee_id = serializers.CharField()
    comment = ZendeskCommentSerializer(many=True)
    tags = ZendeskTagSerializer(many=True)
    custom_fields = ZendeskCustomFieldsSerializer(many=True)
    recipient_email = serializers.EmailField()
    responder = serializers.CharField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    due_at = serializers.CharField()
    # status = serializers.CharField()
    priority = serializers.ChoiceField(
        choices=TICKET_PRIORITIES,
        allow_blank=True,
        default="low",
    )
    assignee_id = serializers.CharField()
    attachments = ZendeskAttachmentSerializer(many=True)


class ZendeskTicketContainer(serializers.Serializer):
    ticket = ZendeskTicketSerializer(many=True)
