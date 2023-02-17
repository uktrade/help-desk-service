import logging

from interfaces import (
    HelpDeskBase,
    HelpDeskComment,
    HelpDeskCustomField,
    HelpDeskException,
    HelpDeskGroup,
    HelpDeskTicket,
    HelpDeskTicketNotFoundException,
    HelpDeskUser,
    Status,
)
from zenpy import Zenpy
from zenpy.lib import exception
from zenpy.lib.api_objects import Comment as ZendeskComment
from zenpy.lib.api_objects import CustomField as ZendeskCustomField
from zenpy.lib.api_objects import Ticket as ZendeskTicket
from zenpy.lib.api_objects import User as ZendeskUser

logger = logging.getLogger(__name__)


class ZendeskClientNotFoundException(Exception):
    pass


class ZendeskManager(HelpDeskBase):
    client = None

    def __init__(self, **kwargs):
        """Create a new Zendesk client - pass credentials to.

        :param credentials: The credentials required to create client { token , email, subdomain }.
        """
        if not kwargs.get("credentials", None):
            raise ZendeskClientNotFoundException("No Zendesk credentials provided")

        self.client = Zenpy(
            timeout=kwargs.get("credentials").get("timeout", 5),
            email=kwargs.get("credentials")["email"],
            token=kwargs.get("credentials")["token"],
            subdomain=kwargs.get("credentials")["subdomain"],
        )

    def get_or_create_user(self, user: HelpDeskUser = None) -> HelpDeskUser:
        """Get or Create a new Zendesk user.   /PS-IGNORE

        :param HelpDeskUser
                full_name: string full name for Zendesk user.
                email: string email address text for the Zendesk user.

        :returns: HelpDeskUser instance representing Zendesk user.
        """
        if user is None:
            transformed_user = self.client.users.me()
        else:
            transformed_user = self.__transform_help_desk_user_to_zendesk_user(user)

        if transformed_user.id:
            zendesk_user = self.client.users(id=transformed_user.id)
        else:
            zendesk_user = self.client.users.create_or_update(transformed_user)

        if zendesk_user is None:
            message = f"No Zendesk user found for {transformed_user}"  # Error log /PS-IGNORE,
            logger.debug(message)
            raise HelpDeskException(message)
        return self.__transform_zendesk_user_to_help_desk_user(zendesk_user)

    def create_ticket(self, ticket: HelpDeskTicket) -> HelpDeskTicket:
        """Create a new Zendesk ticket in response to a new user question.

        :param ticket: HelpDeskTicket with information to create Zendesk ticket.

        :returns: A HelpDeskTicket instance.
        """

        zendesk_audit = self.client.tickets.create(
            self.__transform_help_desk_to_zendesk_ticket(ticket)
        )
        return self.__transform_zendesk_to_help_desk_ticket(zendesk_audit.ticket)

    def get_ticket(self, ticket_id: int) -> HelpDeskTicket:
        """Recover the ticket by Zendesk ID.

        :param ticket_id: The Zendesk ID of the Ticket.

        :returns: A HelpDeskTicket instance.

        :raises:
            HelpDeskTicketNotFoundException: If no ticket is found.
        """
        logger.debug(f"Look for Ticket by is Zendesk ID:<{ticket_id}>")  # /PS-IGNORE
        try:
            return self.__transform_zendesk_to_help_desk_ticket(self.client.tickets(id=ticket_id))
        except exception.RecordNotFoundException:
            message = f"Could not find Zendesk ticket with ID:<{ticket_id}>"  # /PS-IGNORE

            logger.debug(message)
            raise HelpDeskTicketNotFoundException(message)

    def close_ticket(self, ticket_id: int) -> HelpDeskTicket:
        """Close a ticket in Zendesk.

        :param ticket_id: The Zendesk ticket ID.

        :returns: HelpDeskTicket instance.
        """
        logger.debug(f"Looking for ticket with ticket_id:<{ticket_id}>")
        ticket = self.get_ticket(ticket_id)

        if ticket.status == Status.CLOSED:
            logger.warning(f"The ticket:<{ticket.id}> has already been closed!")
        else:
            ticket.status = Status.CLOSED
            ticket = self.update_ticket(ticket)
            logger.debug(f"Closed ticket:<{ticket.id}> for ticket_id:<{ticket_id}>")

        return ticket

    def add_comment(self, ticket_id: int, comment: HelpDeskComment) -> HelpDeskTicket:
        """Add a comment to an existing ticket.

        :param ticket_id: id of Zendesk ticket instance.
        :param comment: HelpDeskComment instance.

        :returns: The updated HelpDeskTicket instance.
        """
        ticket = self.get_ticket(ticket_id)
        ticket.comment = comment
        return self.update_ticket(ticket)

    def update_ticket(self, ticket: HelpDeskTicket) -> HelpDeskTicket:
        """Update an existing ticket.

        :param ticket: HelpDeskTicket ticket.

        :returns: The updated HelpDeskTicket instance.

        :raises:
            HelpDeskTicketNotFoundException: If no ticket is found.
        """
        ticket_audit = self.client.tickets.update(
            self.__transform_help_desk_to_zendesk_ticket(ticket)
        )
        if ticket_audit is None:
            message = f"Could not update ticket with id  {ticket.id}"
            logger.error(message)
            raise HelpDeskTicketNotFoundException(message)

        return self.__transform_zendesk_to_help_desk_ticket(ticket_audit.ticket)

    def __transform_help_desk_to_zendesk_ticket(self, ticket: HelpDeskTicket) -> ZendeskTicket:
        """Transform from HelpDeskTicket to Zendesk ticket instance.

        :param ticket: HelpDeskTicket instance.
        :returns: Zendesk ticket instance.
        """

        custom_fields, comment = None, None
        ticket_user = self.get_or_create_user(ticket.user)

        if ticket.custom_fields:
            custom_fields = [
                ZendeskCustomField(id=custom_field.id, value=custom_field.value)
                for custom_field in ticket.custom_fields
            ]

        if ticket.comment:
            comment = ZendeskComment(
                body=ticket.comment.body,
                author_id=ticket.comment.author_id if ticket.comment.author_id else ticket_user.id,
                public=ticket.comment.public,
            )

        ticket = ZendeskTicket(
            id=ticket.id,
            status=ticket.status,
            recipient=ticket.recipient_email,
            subject=ticket.subject,
            description=ticket.description,
            submitter_id=ticket_user.id,
            assignee_id=ticket.assignee_id,
            requester_id=ticket_user.id,
            group_id=ticket.group_id,
            external_id=ticket.external_id,  # /PS-IGNORE
            priority=ticket.priority,
            tags=ticket.tags,
            custom_fields=custom_fields,
            comment=comment,
        )

        return ticket

    def __transform_zendesk_to_help_desk_ticket(self, ticket: ZendeskTicket) -> HelpDeskTicket:
        """Transform Zendesk ticket into HelpDeskTicket instance.

        :param ticket: Zendesk ticket instance.

        :returns: HelpDeskTicket instance.
        """
        ticket_user, custom_fields, comment = None, None, None

        if getattr(ticket, "requester", None):
            ticket_user = HelpDeskUser(
                id=ticket.requester.id,
                full_name=ticket.requester.name,
                email=ticket.requester.email,
            )
        elif getattr(ticket, "requester_id", None):
            ticket_user = HelpDeskUser(id=ticket.requester_id)

        if getattr(ticket, "custom_fields", None):
            custom_fields = [
                HelpDeskCustomField(id=custom_field["id"], value=custom_field["value"])
                for custom_field in ticket.custom_fields
            ]

        if getattr(ticket, "comment", None):
            comment = HelpDeskComment(
                body=ticket.comment.body,
                author_id=ticket.comment.author_id,
                public=ticket.comment.public,
            )

        help_desk_ticket = HelpDeskTicket(
            id=ticket.id,
            status=getattr(ticket, "status", None),
            recipient_email=getattr(ticket, "recipient", None),
            subject=ticket.subject,
            description=ticket.description,
            user=ticket_user,
            created_at=getattr(ticket, "created_at", None),
            updated_at=getattr(ticket, "updated_at", None),
            priority=getattr(ticket, "priority", None),
            due_at=getattr(ticket, "due_at", None),
            assignee_id=getattr(ticket, "assignee_id", None),
            group_id=getattr(ticket, "group_id", None),
            external_id=getattr(ticket, "external_id", None),  # /PS-IGNORE
            tags=getattr(ticket, "tags", None),
            custom_fields=custom_fields,
            comment=comment,
        )
        return help_desk_ticket

    def __transform_help_desk_user_to_zendesk_user(self, user: HelpDeskUser) -> ZendeskUser:
        """Transform HelpDesk user into Zendesk user.

        :param user: HelpDeskUser instance.

        :returns: ZendeskUser instance.
        """
        if user and user.id:
            return ZendeskUser(id=user.id)
        elif user and user.email:
            return ZendeskUser(name=user.full_name, email=user.email)
        else:
            # This should not be possible so raise exception
            raise HelpDeskException(
                "Cannot transform user to Zendesk user",
            )

    def __transform_zendesk_user_to_help_desk_user(self, user: ZendeskUser) -> HelpDeskUser:
        """Transform HelpDesk user into Zendesk user.

        :param user: HelpDeskUser user instance.

        :returns: ZendeskUser instance.
        """
        groups = [
            HelpDeskGroup(
                created_at=zendesk_group.created_at,
                deleted=zendesk_group.deleted,
                id=zendesk_group.id,
                name=zendesk_group.name,
                updated_at=zendesk_group.updated_at,
                url=zendesk_group.url,
            )
            for zendesk_group in list(self.client.users.groups(user))
        ]

        return HelpDeskUser(id=user.id, full_name=user.name, email=user.email, groups=groups)
