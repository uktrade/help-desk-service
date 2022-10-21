from model_utils import Choices
from rest_framework import serializers

TICKET_PRIORITIES = Choices(
    ("new", "New"),
    ("open", "Open"),
    ("pendign", "Pending"),
    ("on-hold", "On-hold"),
    ("solved", "Solved"),
)


class ChoiceField(serializers.ChoiceField):
    def to_representation(self, obj):
        if obj == "" and self.allow_blank:
            return obj
        return self._choices[obj]

    def to_internal_value(self, data):
        # To support inserts with the value
        if data == "" and self.allow_blank:
            return ""

        for key, val in self._choices.items():
            if val == data:
                return key
        self.fail("invalid_choice", input=data)


class CommentSerializer(serializers.Serializer):
    body = serializers.EmailField()
    public = serializers.CharField(max_length=200)


class TicketSerializer(serializers.Serializer):
    priority = ChoiceField(choices=TICKET_PRIORITIES)
    comment = CommentSerializer(many=True, read_only=True)
    subject = serializers.CharField(max_length=200)
