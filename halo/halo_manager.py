import logging
from typing import List

from halo.halo_api_client import HaloAPIClient, HaloRecordNotFoundException
from halo.data_class import (
    HelpDeskBase,
    HelpDeskComment,
    HelpDeskException,
    HelpDeskTicket,
    HelpDeskTicketNotFoundException,
    HelpDeskUser,
    TicketType,
)


# def reverse_keys(dictionary):
#     return {value: key for key, value in dictionary.items()}


# Zendesk status - Halo status
ZENDESK_TO_HALO_STATUS_MAPPING = {
    "new": [1,4],
    "open": 2,  # in progress
    "pending": 3,  # action requried
    "on-hold": 28,
    "solved": 18,  # approved  ???
    "closed": 9,
}

# REVERSE_STATUS_MAPPING = reverse_keys(STATUS_MAPPING)
PRIORITY_MAPPING = {
    "incident": {"low": 4, "normal": 3, "high": 2, "urgent": 1},
}
# REVERSE_PRIORITY_MAPPING = {key: reverse_keys(value) for key, value in PRIORITY_MAPPING.items()}
# TICKET_TYPE_MAPPING = {
#     1: TicketType.INCIDENT,
#     2: TicketType.INCIDENT,
#     3: TicketType.INCIDENT,
#     24: TicketType.INCIDENT,
#     21: TicketType.INCIDENT,
#     27: TicketType.INCIDENT,
#     28: TicketType.INCIDENT,
#     29: TicketType.INCIDENT,
# }

logger = logging.getLogger(__name__)


class HaloManager(HelpDeskBase):
    def __init__(self, client_id, client_secret):
        """Create a new Halo client - pass credentials to.
        :TODO - correct
        """
        self.client = HaloAPIClient(
            client_id=client_id,
            client_secret=client_secret,
        )

    def get_user(self, id: str):
        halo_user = self.client.get(path=f"Users/{id}")
        # Need to transform into a Zendesk compatible user structure
        zendesk_user = "TODO"
        return zendesk_user

    def create_user(self, user_details: ZendeskUserDetails = {}) -> ZendeskUser:
        # Receive Zendesk user and create user in Halo, give back Zendesk user
        halo_payload = "TODO create payload from incoming Zendesk user details"
        halo_user = self.client.post(path="Users", payload=[halo_payload])
        return halo_user

    def create_ticket(self, ticket_details: ZendeskTicketDetails) -> ZendeskTicket:
        # Create tickert 
        halo_payload = "TODO create payload from incoming Zendesk ticket details"
        halo_response = self.client.post(path="Tickets", payload=[halo_payload])

        zendesk_ticket_response = "TODO populate with transformed Halo response"

        # If we have a comment we have to add it to the ticket after creation
        if ticket_details.comment:
            zendesk_ticket_response["comment"] = self.client.post(
                path="Actions",
                payload="TODO add ticket id and outcome?",
            )

        return zendesk_ticket_response

    # def get_ticket(self, ticket_id: int = None) -> HelpDeskTicket:
    #     """Recover the ticket by Halo ID.
    #     :param ticket_id: The Halo ID of the Ticket.
    #     :returns: A HelpDeskTicket instance.
    #     :raises:
    #         HelpDeskTicketNotFoundException: If no ticket is found.
    #     """
    #     logger.debug(f"Look for Ticket by is Halo ID:<{ticket_id}>")  # /PS-IGNORE
    #     try:
    #         if ticket_id:
    #             return [
    #                 self.__transform_object_to_helpdesk_ticket(
    #                     self.client.get(path=f"Tickets/{ticket_id}")
    #                 )
    #             ]
    #         else:
    #             tickets = self.client.get(path="Tickets")
    #             all_tickets = []
    #             for ticket in tickets["tickets"]:
    #                 helpdesk_ticket = self.__transform_object_to_helpdesk_ticket(ticket)
    #                 all_tickets.append(helpdesk_ticket)
    #             return all_tickets

    #     except HaloRecordNotFoundException:
    #         message = f"Could not find Halo ticket with ID:<{ticket_id}>"  # /PS-IGNORE

    #         logger.debug(message)
    #         raise HelpDeskTicketNotFoundException(message)

    # def close_ticket(self, ticket_id: int) -> HelpDeskTicket:
    #     """Close a ticket in Halo.
    #     :param ticket_id: The Halo ticket ID.
    #     :returns: HelpDeskTicket instance.
    #     """
    #     raise NotImplementedError()

    # def add_comment(self, ticket_id: int, comment: HelpDeskComment) -> HelpDeskTicket:
    #     """Add a comment to an existing ticket.
    #     :param ticket_id: id of Halo ticket instance.
    #     :param comment: HelpDeskComment instance.
    #     :returns: The updated HelpDeskTicket instance.
    #     """
    #     raise NotImplementedError()

    # def update_ticket(self, ticket: HelpDeskTicket) -> HelpDeskTicket:
    #     """Update an existing ticket.
    #     :param ticket: HelpDeskTicket ticket.
    #     :returns: The updated HelpDeskTicket instance.
    #     :raises:
    #         HelpDeskTicketNotFoundException: If no ticket is found.
    #     """
    #     halo_ticket = self.__transform_helpdesk_to_halo_ticket(ticket)
    #     if not ticket.id:
    #         logger.error("No ticket id")
    #         raise HelpDeskTicketNotFoundException("No ticket id")

    #     updated_ticket = self.client.post(path="Tickets", payload=[halo_ticket])
    #     if updated_ticket is None:
    #         message = f"Could not update ticket with id {ticket.id}"
    #         logger.error(message)
    #         raise HelpDeskTicketNotFoundException(message)

    #     if halo_ticket["comment"]:
    #         updated_ticket["comment"] = self.client.post(
    #             path="Actions", payload=[halo_ticket["comment"]]
    #         )

    #     return self.__transform_object_to_helpdesk_ticket(updated_ticket)

    # def get_comments(self, ticket_id: int) -> List[HelpDeskComment]:
    #     comments = []
    #     ticket_actions = self.client.get(f"Actions?ticket_id={ticket_id}")
    #     for action in reversed(ticket_actions["actions"]):
    #         if action["outcome"] == "comment":
    #             comment = self.__transform_halo_action_to_comment(action)
    #             comments.append(comment)
    #     return comments
