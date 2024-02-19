import sentry_sdk
from halo.data_class import ZendeskException
from halo.halo_api_client import HaloClientNotFoundException
from halo.halo_manager import HaloManager
from rest_framework import authentication, permissions, status
from rest_framework.parsers import FileUploadParser
from rest_framework.renderers import BrowsableAPIRenderer, JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from help_desk_api.pagination import CustomPagination
from help_desk_api.serializers import (
    HaloToZendeskCommentSerializer,
    HaloToZendeskTicketContainerSerializer,
    HaloToZendeskTicketsContainerSerializer,
    HaloToZendeskUploadSerializer,
    HaloToZendeskUserSerializer,
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

    serializer_class = HaloToZendeskUserSerializer

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]

    def get(self, request, *args, **kwargs):
        """
        Get a user from Halo
        """
        try:
            halo_user = self.halo_manager.get_user(user_id=self.kwargs.get("id"))
            serializer = HaloToZendeskUserSerializer(halo_user)
            return Response(serializer.data)
        except HaloClientNotFoundException as error:
            sentry_sdk.capture_exception(error)
            return Response(
                "please check userid, a user with given id could not be found",
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request, *args, **kwargs):
        """
        Create a User in Halo
        """
        try:
            halo_response = self.halo_manager.create_user(request.data)
            serializer = HaloToZendeskUserSerializer(halo_response)
            if "id" in request.data:
                # If "id" exists in payload that means we are updating user
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # There is no "id" in payload, so we create a User
                return Response({"user": serializer.data}, status=status.HTTP_201_CREATED)
        except ZendeskException as error:
            sentry_sdk.capture_exception(error)
            return Response(
                "please check payload - user payload must have site id",
                status=status.HTTP_400_BAD_REQUEST,
            )


class MeView(HaloBaseView):
    """
    View for interaction with self
    """

    serializer_class = HaloToZendeskUserSerializer

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]

    def get(self, request, format=None):
        """
        GET Me (self) from Halo
        """
        # TODO:// get the ME user id from zendesk and pass to Halo
        # from zenpy import Zenpy
        # credentials = {
        #     "email": "xyz",
        #     "token": "1234",
        #     "subdomain": "uktrade"
        # }
        # zendesk_manager = Zenpy(**credentials)
        # me_user = zendesk_manager.users.me()
        # print(me_user)
        try:
            zendesk_response = self.halo_manager.get_me(user_id=10745112443421)  # Hardcoded
            serializer = HaloToZendeskUserSerializer(zendesk_response["users"][0])  # Hardcoded
            return Response(serializer.data)
        except ZendeskException as exp:
            sentry_sdk.capture_exception(exp)
            return Response(
                "please check user_id",
                status=status.HTTP_400_BAD_REQUEST,
            )


class CommentView(HaloBaseView):
    """
    View for interaction with comment
    """

    serializer_class = HaloToZendeskCommentSerializer

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]

    def get(self, request, id, format=None):
        """
        GET comments from Halo
        """
        # Get ticket from Halo
        queryset = self.halo_manager.get_comments(ticket_id=id)
        serializer = HaloToZendeskCommentSerializer(queryset, many=True)
        return Response(serializer.data)


class TicketView(HaloBaseView, CustomPagination):
    """
    View for interacting with tickets
    """

    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.AllowAny]
    renderer_classes = [JSONRenderer, BrowsableAPIRenderer]

    def get(self, request, *args, **kwargs):
        """
        GET ticket/tickets from Halo
        """
        # 1. View receives Zendesk compatible request variables
        # 2. View calls manager func with Zendesk class params
        try:
            if "id" in self.kwargs:
                halo_response = self.halo_manager.get_ticket(ticket_id=self.kwargs.get("id"))
                # 4. View uses serializer class to transform Halo format to Zendesk
                serializer = HaloToZendeskTicketContainerSerializer(halo_response)
                # 5. Serialized data (in Zendesk format) sent to caller
                return Response(serializer.data)
            else:
                # pagenum = self.request.query_params.get("page", None)
                tickets = self.halo_manager.get_tickets()
                pages = self.paginate_queryset(tickets["tickets"], self.request)
                # 4. View uses serializer class to transform Halo format to Zendesk
                serializer = HaloToZendeskTicketsContainerSerializer({"tickets": pages})
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
            if "ticket_id" in request.data:
                zendesk_ticket = self.halo_manager.update_ticket(request.data)
                # 4. View uses serializer class to transform Halo format to Zendesk
                serializer = HaloToZendeskTicketContainerSerializer(zendesk_ticket)
                # 5. Serialized data (in Zendesk format) sent to caller
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                zendesk_ticket_data = request.data
                zendesk_ticket_data["zendesk_ticket_id"] = getattr(
                    request, "zendesk_ticket_id", None
                )
                zendesk_ticket = self.halo_manager.create_ticket(request.data)
                # 4. View uses serializer class to transform Halo format to Zendesk
                serializer = HaloToZendeskTicketContainerSerializer(zendesk_ticket)
                # 5. Serialized data (in Zendesk format) sent to caller
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ZendeskException:
            return Response(
                "please check payload - " "create ticket payload must have ticket and comment",
                status=status.HTTP_400_BAD_REQUEST,
            )

    def put(self, request, *args, **kwargs):
        """
        Data Workspace uses `update` to add a private note to
        a dataset access request ticket after creation.
        Zenpy uses PUT for `update`.
        """
        ticket_id = kwargs.get("id", None)
        if ticket_id is None:
            # Shouldn't get here as URL routing ought to have provided it.
            # But just in case…
            return Response(
                "Ticket ID is required for HTTP PUT request",
                status=status.HTTP_400_BAD_REQUEST,
            )
        ticket_data = request.data.get("ticket", {})
        comment_data = ticket_data.get("comment", {})
        comment_body = comment_data.get("body", None)
        if comment_body is not None:
            # Halo adds comments differently to Zendesk
            halo_response = self.halo_manager.add_comment(request.data)
            return Response(halo_response, status=status.HTTP_200_OK)
        else:
            # Nothing gets here at present, but something might one day
            return Response(
                f"Unexpected PUT to {request.path} without comment",
                status=status.HTTP_400_BAD_REQUEST,
            )


class UploadsView(HaloBaseView):
    """
    View for uploading attachments
    """

    parser_classes = [
        FileUploadParser,
    ]

    def post(self, request, *args, **kwargs):
        try:
            filename = request.query_params.get("filename", None)
            data = request.body
            halo_response = self.halo_manager.upload_file(
                filename=filename,
                data=data,
                content_type=request.headers.get("Content-Type", "text/plain"),
            )
            serializer = HaloToZendeskUploadSerializer(halo_response)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ZendeskException as error:
            sentry_sdk.capture_exception(error)
            return Response(
                "File upload failed",
                status=status.HTTP_400_BAD_REQUEST,
            )
