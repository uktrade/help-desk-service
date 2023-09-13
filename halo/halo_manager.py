import base64
import logging

from django.conf import settings
from halo.data_class import ZendeskException, ZendeskTicketNotFoundException
from halo.halo_api_client import HaloAPIClient, HaloRecordNotFoundException

from help_desk_api.serializers import (
    ZendeskToHaloCreateCommentSerializer,
    ZendeskToHaloCreateTicketSerializer,
    ZendeskToHaloCreateUserSerializer,
    ZendeskToHaloUpdateCommentSerializer,
    ZendeskToHaloUpdateTicketSerializer,
    ZendeskToHaloUpdateUserSerializer,
)


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

    def get_user(self, user_id: int) -> dict:
        halo_response = self.client.get(path=f"Users/{user_id}")
        return halo_response

    def get_users(self):
        halo_response = self.client.get(path="Users/")
        return halo_response

    def create_user(self, zendesk_request: dict = None) -> dict:
        """
        Receive Zendesk user and create user in Halo, give back Zendesk user.
        If you need to create users without sending out a verification email,
        include a "skip_verify_email": true property.
        If you don't specify a role parameter, the new user is assigned the role of end user.
        """
        halo_user = ZendeskToHaloCreateUserSerializer(zendesk_request)
        halo_response = self.client.post(path="Users", payload=[halo_user.data])
        return halo_response

    def update_user(self, zendesk_request: dict = None) -> dict:
        """
        Receive Zendesk user and update user in Halo, give back Zendesk user.
        """
        halo_user = ZendeskToHaloUpdateUserSerializer(zendesk_request)
        halo_response = self.client.post(path="Users", payload=[halo_user.data])
        return halo_response

    def get_me(self, user_id: int):
        halo_user = self.client.get(path=f"Users?search={user_id}")
        return halo_user

    def get_ticket(self, ticket_id: int = None) -> dict:
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

            return {"ticket": [halo_response]}
        except HaloRecordNotFoundException:
            message = f"Could not find Halo ticket with ID:<{ticket_id}>"  # /PS-IGNORE

            logger.debug(message)
            raise ZendeskTicketNotFoundException(message)

    def create_ticket(self, zendesk_request: dict = None) -> dict:
        # Create ticket
        # 3. Manager calls Halo API and returns Halo flavoured return value
        if zendesk_request is None:
            zendesk_request = {}
        if "ticket" in zendesk_request and "comment" in zendesk_request["ticket"]:
            halo_payload = ZendeskToHaloCreateTicketSerializer(zendesk_request)
            halo_response = self.client.post(path="Tickets", payload=[halo_payload.data])

            zendesk_request["ticket_id"] = halo_response["id"]
            comment_payload = ZendeskToHaloCreateCommentSerializer(zendesk_request)
            actions_response = self.client.post(path="Actions", payload=[comment_payload.data])

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
        else:
            logging.error("create ticket payload must have ticket and comment")
            raise ZendeskException

        return {"ticket": [halo_response]}

    def update_ticket(self, zendesk_request: dict = None) -> dict:
        """Update an existing ticket.
        :param zendesk_request: HelpDeskTicket ticket.
        :returns: The updated HelpDeskTicket instance.
        :raises:
            HelpDeskTicketNotFoundException: If no ticket is found.
        """
        if zendesk_request is None:
            zendesk_request = {}
        halo_payload = ZendeskToHaloUpdateTicketSerializer(zendesk_request)
        updated_ticket = self.client.post(path="Tickets", payload=[halo_payload.data])
        if updated_ticket is None:
            message = f"Could not update ticket with id {zendesk_request['id']}"
            logger.error(message)
            raise ZendeskTicketNotFoundException(message)

        if "ticket" in zendesk_request and "comment" in zendesk_request["ticket"]:
            if "id" in zendesk_request["ticket"]["comment"]:
                zendesk_request["ticket_id"] = updated_ticket["id"]
                comment_payload = ZendeskToHaloUpdateCommentSerializer(zendesk_request)
                updated_ticket["comment"] = [
                    self.client.post(path="Actions", payload=[comment_payload.data])
                ]
            else:
                zendesk_request["ticket_id"] = updated_ticket["id"]
                comment_payload = ZendeskToHaloCreateCommentSerializer(zendesk_request)
                updated_ticket["comment"] = [
                    self.client.post(path="Actions", payload=[comment_payload.data])
                ]

        return {"ticket": [updated_ticket]}

    def get_comments(self, ticket_id: int) -> list[dict]:
        comments = []
        ticket_actions = self.client.get(f"Actions?ticket_id={ticket_id}")
        for action in reversed(ticket_actions["actions"]):
            if action["outcome"] == "comment":
                # zendesk_comment = ZendeskComment(**action)
                comments.append(action)
        return comments

    def get_tickets(self) -> dict:
        """
        GET All Tickets from Halo
        """
        # params for payload
        params = {
            "pageinate": "true",
            "page_size": settings.REST_FRAMEWORK["PAGE_SIZE"],
            "page_no": 1,
        }
        halo_response = self.client.get(path="Tickets", params=params)
        page_size = halo_response["page_size"]
        record_count = halo_response["record_count"]
        pages = record_count // page_size
        # TODO: Logic based on page number rather than calling GET multiple times.
        all_tickets = []
        for i in range(1, pages + 2):
            params["page_no"] = i
            halo_response = self.client.get(path="Tickets", params=params)
            all_tickets.extend(halo_response["tickets"])
        halo_response["tickets"] = all_tickets

        return halo_response

    def upload_file(self, filename: str, data: bytes):
        params = {
            "filename": filename,
            "data_base64": base64.b64encode(data).decode("ascii"),  # /PS-IGNORE
        }
        halo_response = self.client.post(path="Attachment", payload=params)
        return halo_response
