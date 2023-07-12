import logging
import os

from scripts.utils import utils


class HaloToZendesk:
    """
    This is a mapping class, where we map the Halo response to Zendesk response
    """

    def get_ticket_response_mapping(self, ticket_response):
        """
        Ticket Mapping
        """
        mapped_data = utils.read_mapping(os.path.join(os.getcwd(), "config/mapping.json"))
        zendesk_response = {
            "id": ticket_response["id"],
            "subject": ticket_response.get(mapped_data["subject"], ""),
            "details": ticket_response.get("details", ""),
            "user": ticket_response.get("user", {}),
            "group_id": ticket_response["id"],
            "external_id": ticket_response["id"],
            "assignee_id": ticket_response["user_id"],
            "comment": ticket_response.get("comment", []),
            "tags": [tag.get("text", "") for tag in ticket_response.get("tags", [])],
            "custom_fields": ticket_response.get("customfields", []),
            "recipient_email": ticket_response.get("user_email", ""),
            "responder": ticket_response.get("reportedby", ""),
            "created_at": ticket_response["dateoccurred"],
            "updated_at": ticket_response["dateoccurred"],
            "due_at": ticket_response["deadlinedate"],
            # "status": ticket_response['id'],
            # "priority": ticket_response["priority"]["name"],
            "ticket_type": "incident",  # ticket_response['tickettype']['name'],
            "attachments": ticket_response.get("attachments", []),
        }
        return zendesk_response

    def get_tickets_response_mapping(self, ticket_response):
        """
        List Tickets with Pagination Logic
        """
        halo_response = {}
        halo_response["page_no"] = ticket_response["page_no"]
        halo_response["page_size"] = ticket_response["page_size"]
        halo_response["record_count"] = ticket_response["record_count"]
        all_tickets = []
        if "tickets" in ticket_response:
            for ticket in ticket_response["tickets"]:
                zendesk_response = self.get_ticket_response_mapping(ticket)
                all_tickets.append(zendesk_response)
        halo_response["tickets"] = all_tickets

        return halo_response

    def get_user_me_response_mapping(self, user_response):
        """
        User mapping from Halo to Zendesk
        """
        # TODO:// if more than one user handle case differently
        zendesk_user = {}
        if user_response["record_count"] == 1:
            if "users" in user_response:
                for user in user_response["users"]:
                    zendesk_user["id"] = user["id"]
                    zendesk_user["name"] = user["name"]
                    zendesk_user["email"] = user["emailaddress"]
        else:
            logging.error("Other 5 is not set or is set on multiple fields")
        return zendesk_user

    def get_user_response_mapping(self, user_response):
        """
        We convert Halo response to Zendesk response
        """
        if "emailaddress" in user_response:
            user_response["email"] = user_response["emailaddress"]
        return user_response
