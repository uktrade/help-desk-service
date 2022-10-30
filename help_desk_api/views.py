from rest_framework.response import Response
from rest_framework.views import APIView

from help_desk_api.serializers import TicketContainer


class UserView(APIView):
    """
    View for interaction with tickets
    """

    def get(self, request, format=None):
        """
        Return a ticket
        """
        # Get ticket from Halo

        return Response()

    def post(self, request, format=None):
        """
        Return a ticket
        """
        # Get ticket from Halo

        return Response()


class MeView(APIView):
    """
    View for interaction with tickets
    """

    def get(self, request, format=None):
        """
        Return a ticket
        """
        # Get ticket from Halo

        return Response()


class CommentView(APIView):
    """
    View for interaction with tickets
    """

    def get(self, request, format=None):
        """
        Return a ticket
        """
        # Get ticket from Halo

        return Response()


class TicketView(APIView):
    """
    View for interaction with tickets
    """

    def get(self, request, id, format=None):
        """
        Return a ticket
        """
        # Get ticket from Halo

        # snippet = self.get_object(pk)
        # serializer = SnippetSerializer(snippet)
        # return Response(serializer.data)

        return Response()

    def put(self, request, id, format=None):
        # snippet = self.get_object(pk)
        # serializer = SnippetSerializer(snippet, data=request.data)
        # if serializer.is_valid():
        #     serializer.save()
        #     return Response(serializer.data)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response()

    def post(self, request, format=None):
        """
        Create a ticket
        """
        ticket_serializer = TicketContainer(data=request.data)

        if ticket_serializer.is_valid(raise_exception=True):
            ticket_serializer.save()

        return Response()
