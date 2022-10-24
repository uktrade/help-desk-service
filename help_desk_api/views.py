from rest_framework.response import Response
from rest_framework.views import APIView

from help_desk_api.serializers import TicketContainer


class TicketView(APIView):
    """
    View for interaction with tickets
    """

    def get(self, request, format=None):
        """
        Return a list of all tickets.
        """
        return Response()

    def post(self, request, format=None):
        """
        Create a ticket
        """
        ticket_serializer = TicketContainer(data=request.data)

        if ticket_serializer.is_valid(raise_exception=True):
            ticket_serializer.save()

        return Response()
