from rest_framework.response import Response
from rest_framework.views import APIView

from help_desk_api.serializers import TicketContainer
from help_desk_api.utils import http_verb


class TicketView(APIView):
    """
    View for interaction with tickets
    """

    @http_verb(verb="POST")
    def post(self, request, format=None):
        """
        Create a ticket
        """
        ticket_serializer = TicketContainer(data=request.data)

        if ticket_serializer.is_valid(raise_exception=True):
            ticket_serializer.save()

        return Response()
