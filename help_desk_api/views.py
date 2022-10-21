from rest_framework.response import Response
from rest_framework.views import APIView


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
        return Response()
