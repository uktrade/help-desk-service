from halo.halo_manager import HaloManager
from halo.interfaces import HelpDeskTicket, HelpDeskUser
from rest_framework.response import Response
from rest_framework.views import APIView

from help_desk_api.serializers import TicketContainer


class HaloBaseView(APIView):
    """
    Base view for Halo interaction
    """

    def initial(self, request, *args, **kwargs):
        request.help_desk_creds

        self.halo_manager = HaloManager(
            client_id=request.help_desk_creds.halo_client_id,
            client_secret=request.help_desk_creds.halo_client_secret,
        )


class UserView(HaloBaseView):
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


class MeView(HaloBaseView):
    """
    View for interaction with tickets
    """

    def get(self, request, format=None):
        """
        Return a ticket
        """
        # Get ticket from Halo

        return Response()


class CommentView(HaloBaseView):
    """
    View for interaction with tickets
    """

    def get(self, request, format=None):
        """
        Return a ticket
        """
        # Get ticket from Halo

        return Response()


class TicketView(HaloBaseView):
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
            help_desk_user = HelpDeskUser(
                id=36,
            )

            ticket = HelpDeskTicket(
                subject=ticket_serializer.validated_data["ticket"]["subject"],
                description=ticket_serializer.validated_data["ticket"]["description"],
                # priority=ticket_serializer.validated_data["ticket"]["priority"],
                user=help_desk_user,
            )
            result = self.halo_manager.create_ticket(
                ticket,
            )

            print("RESULT")
            print(result)

        return Response("success")
