from halo.halo_manager import HaloManager
from halo.interfaces import HelpDeskTicket, HelpDeskUser
from rest_framework import authentication, permissions, status
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from help_desk_api.serializers import (
    CommentSerializer,
    HaloUserSerializer,
    TicketSerializer,
)


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
    View for interaction with user
    """

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]

    def get(self, request, *args, **kwargs):
        """
        GET User in Halo
        """
        # Build User based on ID

        if self.kwargs.get("id"):
            user = HelpDeskUser(id=self.kwargs.get("id"))
            # Get User from Halo
            queryset = self.halo_manager.get_or_create_user(user, request.method)
            serializer = HaloUserSerializer(queryset)
            return Response(serializer.data)
        else:
            # if no user id is passed we show the agent me??
            return Response()

    def post(self, request, *args, **kwargs):
        """
        CREATE/UPDATE a User in Halo
        """
        # Create/Update User in Halo
        user = HelpDeskUser(
            full_name=request.data["name"],
            email=request.data["emailaddress"],
        )
        if "id" in request.data:
            user.id = request.data["id"]
            queryset = self.halo_manager.get_or_create_user(user, request.method)
        else:
            user.site_id = request.data["site_id"]
            queryset = self.halo_manager.get_or_create_user(user, request.method)
        serializer = HaloUserSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MeView(HaloBaseView):
    """
    View for interaction with self
    """

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]

    def get(self, request, format=None):
        """
        GET Agent Me in Halo
        """
        # Get Me from Halo
        queryset = self.halo_manager.get_or_create_user(user=None)
        serializer = HaloUserSerializer(queryset)
        return Response(serializer.data)


class CommentView(HaloBaseView):
    """
    View for interaction with comment
    """

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]

    def get(self, request, id, format=None):
        """
        GET comments from Halo
        """
        # Get ticket from Halo
        queryset = self.halo_manager.get_comments(ticket_id=id)
        serializer = CommentSerializer(queryset, many=True)
        return Response(serializer.data)


class TicketView(HaloBaseView):
    """
    View for interacting with tickets
    """

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    serializer_class = TicketSerializer
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]

    def get(self, request, *args, **kwargs):
        """
        GET ticket/tickets from Halo
        """
        if self.kwargs.get("id"):
            queryset = self.halo_manager.get_ticket(ticket_id=self.kwargs.get("id"))
        else:
            queryset = self.halo_manager.get_ticket()
        serializer = TicketSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """
        CREATE/UPDATE ticket in Halo
        """
        ticket = HelpDeskTicket(
            subject=request.data["subject"],
            description=request.data["description"],
            priority=request.data["priority"],
            comment=request.data["comment"],
            user=None,
        )

        if "id" in request.data:
            # update the ticket
            ticket.id = request.data["id"]
            queryset = self.halo_manager.update_ticket(
                ticket,
            )
        else:
            queryset = self.halo_manager.create_ticket(
                ticket,
            )
        serializer = TicketSerializer(queryset)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
