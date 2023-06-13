from rest_framework import serializers

TICKET_PRIORITIES = (
    ("low", "Low"),
    ("medium", "Medium"),
    ("high", "High"),
    ("critical", "Critical"),
)


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

    priority = serializers.ChoiceField(
        choices=TICKET_PRIORITIES,
        allow_blank=True,
        default="low",
    )
    # priority = serializers.CharField()
    comment = ZendeskCommentSerializer(many=True)
    subject = serializers.CharField(max_length=200)
    details = serializers.CharField(max_length=200)
    tags = ZendeskTagSerializer(many=True)
    id = serializers.IntegerField()
    attachments = ZendeskAttachmentSerializer(many=True)


class ZendeskTicketContainer(serializers.Serializer):
    ticket = ZendeskTicketSerializer(many=True)

    def create(self, validated_data):
        pass
        # ticket = HelpDeskTicket(
        #     subject=validated_data["ticket"]["subject"],
        #     description=validated_data["ticket"]["description"],
        #     priority=validated_data["ticket"]["priority"],
        # )
        # help_desk.create_ticket(ticket)
        # return validated_data


class ZendeskUserSerializer(serializers.Serializer):
    """
    Halo User Serializer
    """

    id = serializers.IntegerField()
    full_name = serializers.CharField()
    email = serializers.EmailField()

    def to_representation(self, instance):
        zendesk_user = {
            "id": instance["id"],
            "full_name": instance["name"],
            "email": instance["emailaddress"],
        }
        return super().to_representation(zendesk_user)
