from rest_framework import serializers

TICKET_PRIORITIES = (
    ("new", "New"),
    ("open", "Open"),
    ("pendign", "Pending"),
    ("on-hold", "On-hold"),
    ("solved", "Solved"),
)


class ZendeskCommentSerializer(serializers.Serializer):
    """
    Comments Serializer
    """

    body = serializers.CharField()
    public = serializers.BooleanField(default=True)


class ZendeskTicketSerializer(serializers.Serializer):
    """
    Tickets Serializer
    """

    priority = serializers.ChoiceField(
        choices=TICKET_PRIORITIES,
        allow_blank=True,
        default="new",
    )
    comment = CommentSerializer(many=True)
    subject = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=200)
    id = serializers.IntegerField()


class TicketContainer(serializers.Serializer):
    ticket = TicketSerializer()

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
