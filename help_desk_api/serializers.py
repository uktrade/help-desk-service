from django.conf import settings
from rest_framework import serializers

from help_desk_client import get_help_desk_interface
from help_desk_client.interfaces import HelpDeskTicket

TICKET_PRIORITIES = (
    ("new", "New"),
    ("open", "Open"),
    ("pendign", "Pending"),
    ("on-hold", "On-hold"),
    ("solved", "Solved"),
)

help_desk_interface = get_help_desk_interface(settings.HELP_DESK_INTERFACE)
help_desk = help_desk_interface(credentials=settings.HELP_DESK_CREDS)


class CommentSerializer(serializers.Serializer):
    body = serializers.EmailField()
    public = serializers.CharField(max_length=200)


class TicketSerializer(serializers.Serializer):
    priority = serializers.ChoiceField(
        choices=TICKET_PRIORITIES,
        allow_blank=True,
        default="new",
    )
    comment = CommentSerializer(many=True, read_only=True)
    subject = serializers.CharField(max_length=200)
    description = serializers.CharField(max_length=200)


class TicketContainer(serializers.Serializer):
    ticket = TicketSerializer()

    def create(self, validated_data):
        ticket = HelpDeskTicket(
            subject=validated_data["ticket"]["subject"],
            description=validated_data["ticket"]["description"],
            priority=validated_data["ticket"]["priority"],
        )
        help_desk.create_ticket(ticket)
        return validated_data
