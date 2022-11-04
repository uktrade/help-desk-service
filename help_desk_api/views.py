from halo.halo_manager import HaloManager
from halo.interfaces import HelpDeskTicket, HelpDeskUser
from rest_framework.response import Response
from rest_framework.views import APIView

from help_desk_api.serializers import TicketContainer, UserContainer


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

    def get(self, request, id, format=None):
        """
        Return a user
        """
        # Get user from Halo
        help_desk_user = HelpDeskUser(
            id=id,
        )
        result = self.halo_manager.get_user(help_desk_user)

        print("RESULT")
        print(result)
        return Response("success")

    def post(self, request, format=None):
        """
        Return a user
        """
        help_desk_user = HelpDeskUser(
            id=request.data["user"].get("id"),
            full_name=request.data["user"].get("name"),
            email=request.data["user"].get("email"),
        )
        get_user = self.halo_manager.get_user(help_desk_user)
        user_serializer = UserContainer(get_user,data=request.data)

        if user_serializer.is_valid(raise_exception=True):
            user = HelpDeskUser(
                id=user_serializer.validated_data["user"].get("id"),
                full_name=user_serializer.validated_data["user"].get("name"),
                email=user_serializer.validated_data["user"].get("email")
            )
            result = self.halo_manager.create_or_update_user(
                user
            )

            print("RESULT")
            print(result)

        return Response("success")


class MeView(HaloBaseView):
    """
    View for interaction with tickets
    """

    def get(self, request, format=None):
        """
        Return a ticket
        """
        # Get ticket from Halo
        
        result = self.halo_manager.get_current_user()

        print("RESULT")
        print(result)
        return Response("success")


class CommentView(HaloBaseView):
    """
    View for interaction with tickets
    """

    def get(self, request, id,format=None):
        """
        Return a ticket
        """
        result = self.halo_manager.get_comments(id)
        #TODO transform back to zenpy form

        print("RESULT")
        print(result)
        return Response("success")


class TicketView(HaloBaseView):
    def get(self, request, id, format=None):
        """
        Return a ticket
        """
        # Get ticket from Halo

        result = self.halo_manager.get_ticket(id)

        print("RESULT")
        print(result)
        return Response("success")

    def put(self, request, id, format=None):

        current_data = self.halo_manager.get_ticket(id)
        ticket_serializer = TicketContainer(current_data, data=request.data)

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
            result = self.halo_manager.update_ticket(
                ticket,
            )

            print("RESULT")
            print(result)

        return Response("success")

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
