from halo.data_class import ZendeskException
from halo.halo_api_client import HaloClientNotFoundException
from halo.halo_manager import HaloManager
from rest_framework import authentication, permissions, status
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from help_desk_api.pagination import CustomPagination
from help_desk_api.serializers import (
    ZendeskCommentSerializer,
    ZendeskTicketContainerSerializer,
    ZendeskTicketsContainerSerializer,
    ZendeskTicketSerializer,
    ZendeskUserSerializer,
)


class HaloBaseView(APIView):
    """
    Base view for Halo interaction
    """

    def initial(self, request, *args, **kwargs):
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
    serializer_class = ZendeskUserSerializer

    def get(self, request, *args, **kwargs):
        """
        Get a user from Halo
        """
        # Build User based on ID

        if self.kwargs.get("id"):
            # Get User from Halo
            halo_user = self.halo_manager.get_user(user_id=self.kwargs.get("id"))
            serializer = ZendeskUserSerializer(id=halo_user["id"])
            return Response(serializer.data)
        else:
            # if no user id is passed we show the agent me??
            return Response()

    def post(self, request, *args, **kwargs):
        """
        Create a User in Halo
        """
        # Create user in Halo
        halo_user = self.halo_manager.create_user(request.data)  # ** maybe?
        serializer = ZendeskUserSerializer(halo_user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# class MeView(HaloBaseView):
#     """
#     View for interaction with self
#     """

#     authentication_classes = [authentication.TokenAuthentication]
#     permission_classes = [permissions.AllowAny]
#     renderer_classes = [BrowsableAPIRenderer, JSONRenderer]

#     def get(self, request, format=None):
#         """
#         GET Agent Me in Halo
#         """
#         # Get Me from Halo
#         queryset = self.halo_manager.get_or_create_user(user=None)
#         serializer = HaloUserSerializer(queryset)
#         return Response(serializer.data)


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
        serializer = ZendeskCommentSerializer(queryset, many=True)
        return Response(serializer.data)


class TicketView(HaloBaseView, CustomPagination):
    """
    View for interacting with tickets
    """

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    serializer_class = ZendeskTicketSerializer
    renderer_classes = [BrowsableAPIRenderer, JSONRenderer]

    def get(self, request, *args, **kwargs):
        """
        GET ticket/tickets from Halo
        """
        # 1. View receives Zendesk compatible request variables
        # 2. View calls manager func with Zendesk class params
        try:
            if "id" in self.kwargs:
                ticket = self.halo_manager.get_ticket(ticket_id=self.kwargs.get("id"))
                # 4. View uses serializer class to transform Halo format to Zendesk
                serializer = ZendeskTicketContainerSerializer(ticket)
                # 5. Serialized data (in Zendesk format) sent to caller
                return Response(serializer.data)
            else:
                pagenum = self.request.query_params.get("page", None)
                # print(pagenum)
                tickets = self.halo_manager.get_tickets(pagenum=pagenum)
                pages = self.paginate_queryset(tickets.tickets, self.request)
                # 4. View uses serializer class to transform Halo format to Zendesk
                serializer = ZendeskTicketsContainerSerializer({"tickets": pages})
                # 5. Serialized data (in Zendesk format) sent to caller
                return self.get_paginated_response(serializer.data)

        except HaloClientNotFoundException:
            return Response(
                "please check ticket_id - " "a ticket with given id could not be found",
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request, *args, **kwargs):
        """
        CREATE/UPDATE ticket in Halo
        """
        # 1. View receives Zendesk compatible request variables
        # 2. View calls manager func with Zendesk class params
        try:
            if "id" in request.data:
                zendesk_ticket = self.halo_manager.update_ticket(request.data)
                # 4. View uses serializer class to transform Halo format to Zendesk
                serializer = ZendeskTicketContainerSerializer(zendesk_ticket)
                # 5. Serialized data (in Zendesk format) sent to caller
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                zendesk_ticket = self.halo_manager.create_ticket(request.data)
                # 4. View uses serializer class to transform Halo format to Zendesk
                serializer = ZendeskTicketContainerSerializer(zendesk_ticket)
                # 5. Serialized data (in Zendesk format) sent to caller
                return Response(serializer.data, status=status.HTTP_200_OK)
        except ZendeskException:
            return Response(
                "please check payload - " "create ticket payload must have ticket and comment",
                status=status.HTTP_400_BAD_REQUEST,
            )
