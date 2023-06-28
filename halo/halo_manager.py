import logging

from halo.data_class import (
    ZendeskComment,
    ZendeskException,
    ZendeskTicketContainer,
    ZendeskTicketNotFoundException,
    ZendeskTicketsContainer,
)
from halo.halo_api_client import HaloAPIClient, HaloRecordNotFoundException
from halo.halo_to_zendesk import HaloToZendesk
from halo.zendesk_to_halo import ZendeskToHalo

# from typing import List


def reverse_keys(dictionary):
    return {value: key for key, value in dictionary.items()}


# Zendesk status - Halo status
ZENDESK_TO_HALO_STATUS_MAPPING = {
    "new": 1,
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


class HaloManager:
    def __init__(self, client_id, client_secret):
        """Create a new Halo client - pass credentials to.
        :TODO - correct
        """
        self.client = HaloAPIClient(
            client_id=client_id,
            client_secret=client_secret,
        )

    def get_user(self, user_id: int):
        halo_user = self.client.get(path=f"Users/{user_id}")
        # Need to transform into a Zendesk compatible user structure
        zendesk_user = halo_user
        return zendesk_user

    # def create_user(self, user_details: ZendeskUserDetails = {}) -> ZendeskUser:
    #     # Receive Zendesk user and create user in Halo, give back Zendesk user
    #     halo_payload = "TODO create payload from incoming Zendesk user details"
    #     halo_user = self.client.post(path="Users", payload=[halo_payload])
    #     return halo_user

    def create_ticket(self, zendesk_request: dict = {}) -> ZendeskTicketContainer:
        # Create ticket
        # 3. Manager calls Halo API and returns Halo flavoured return value
        zendesk_ticket = None
        if "ticket" in zendesk_request and "comment" in zendesk_request["ticket"]:
            halo_payload = ZendeskToHalo().create_ticket_payload(zendesk_request)
            halo_response = self.client.post(path="Tickets", payload=[halo_payload])
            comment_payload = ZendeskToHalo().create_comment_payload(
                halo_response["id"], zendesk_request
            )
            actions_response = self.client.post(path="Actions", payload=[comment_payload])
            halo_response["comment"] = [actions_response]
            # if attachements exist upload them
            if "attachments" in zendesk_request["ticket"]:
                attachment_payload = zendesk_request["ticket"]["attachments"]
                attachment_payload["ticket_id"] = halo_response["id"]
                halo_response["attachments"] = [
                    self.client.post(
                        f"Attachment?ticket_id={halo_response['id']}", payload=[attachment_payload]
                    )
                ]
            # convert Halo response to Zendesk response
            zendesk_response = HaloToZendesk().get_ticket_response_mapping(halo_response)
            zendesk_ticket = ZendeskTicketContainer(**zendesk_response)
        else:
            logging.error("create ticket payload must have ticket and comment")
            raise ZendeskException

        return zendesk_ticket

    def get_ticket(self, ticket_id: int = None) -> ZendeskTicketContainer:
        """Recover the ticket by Halo ID.
        :param ticket_id: The Halo ID of the Ticket.
        :returns: A HelpDeskTicket instance.
        :raises:
            HelpDeskTicketNotFoundException: If no ticket is found.
        """
        logger.debug(f"Look for Ticket by is Halo ID:<{ticket_id}>")  # /PS-IGNORE
        try:
            # 3. Manager calls Halo API and
            # returns Halo flavoured return value
            halo_response = self.client.get(path=f"Tickets/{ticket_id}")
            ticket_actions = self.client.get(
                f"Actions?ticket_id={halo_response['id']}"
            )  # /PS-IGNORE5
            comment_list = []
            for comment in ticket_actions["actions"]:
                if comment["outcome"] == "comment":
                    comment_list.append(comment)
            halo_response["comment"] = comment_list
            attachments = self.client.get(f"Attachment?ticket_id={halo_response['id']}")
            halo_response["attachments"] = attachments["attachments"]

            # convert Halo response to Zendesk response
            response = HaloToZendesk().get_ticket_response_mapping(halo_response)
            zendesk_response = {"ticket": [response]}
            zendesk_ticket = ZendeskTicketContainer(**zendesk_response)

            return zendesk_ticket
        except HaloRecordNotFoundException:
            message = f"Could not find Halo ticket with ID:<{ticket_id}>"  # /PS-IGNORE

            logger.debug(message)
            raise ZendeskTicketNotFoundException(message)

    def update_ticket(self, zendesk_request: dict = {}) -> ZendeskTicketContainer:
        """Update an existing ticket.
        :param ticket: HelpDeskTicket ticket.
        :returns: The updated HelpDeskTicket instance.
        :raises:
            HelpDeskTicketNotFoundException: If no ticket is found.
        """
        halo_payload = ZendeskToHalo().create_ticket_payload(zendesk_request)
        halo_payload["id"] = zendesk_request["id"]
        updated_ticket = self.client.post(path="Tickets", payload=[halo_payload])
        if updated_ticket is None:
            message = f"Could not update ticket with id {zendesk_request['id']}"
            logger.error(message)
            raise ZendeskTicketNotFoundException(message)

        if "comment" in zendesk_request["ticket"]:
            comment_payload = ZendeskToHalo().update_comment_payload(zendesk_request)
            updated_ticket["comment"] = [
                self.client.post(path="Actions", payload=[comment_payload])
            ]
        # convert Halo response to Zendesk response
        zendesk_response = HaloToZendesk().get_ticket_response_mapping(updated_ticket)
        zendesk_ticket = ZendeskTicketContainer(**zendesk_response)
        return zendesk_ticket

    def get_comments(self, ticket_id: int) -> list[ZendeskComment]:
        comments = []
        ticket_actions = self.client.get(f"Actions?ticket_id={ticket_id}")
        for action in reversed(ticket_actions["actions"]):
            if action["outcome"] == "comment":
                comment = HaloToZendesk().get_comment_response_mapping(action)
                zendesk_comment = ZendeskComment(**comment)
                comments.append(zendesk_comment)
        return comments

    def get_tickets(self, pagenum: int = None) -> ZendeskTicketsContainer:
        params = {
            "pageinate": "true",
            "page_size": 100,
            "page_no": 1,
        }
        halo_response = self.client.get(path="Tickets", params=params)
        # page_no = halo_response["page_no"]
        page_size = halo_response["page_size"]
        record_count = halo_response["record_count"]
        pages = record_count // page_size

        all_tickets = []
        for i in range(1, pages + 2):
            params["page_no"] = i
            halo_response = self.client.get(path="Tickets", params=params)
            all_tickets.extend(halo_response["tickets"])
        print(len(all_tickets))
        halo_response["tickets"] = all_tickets
        # convert Halo response to Zendesk response
        zendesk_response = HaloToZendesk().get_tickets_response_mapping(halo_response)
        zendesk_ticket = ZendeskTicketsContainer(**zendesk_response)

        return zendesk_ticket
