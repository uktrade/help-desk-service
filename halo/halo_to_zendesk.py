class HaloToZendesk:
    """
    This is a mapping class, where we map the Halo response to Zendesk response
    """

    def get_ticket_response_mapping(self, ticket_response):
        """
        Ticket Mapping
        """
        zendesk_response = {
            "ticket": [
                {
                    "id": ticket_response["id"],
                    "subject": ticket_response["summary"],
                    "details": ticket_response["details"],
                    "user": [ticket_response["user"]],
                    "group_id": ticket_response["id"],
                    "external_id": ticket_response["id"],
                    "assignee_id": ticket_response["user_id"],
                    "comment": ticket_response.get("comment", []),
                    "tags": ticket_response.get("tags", []),
                    "custom_fields": ticket_response["customfields"],
                    "recipient_email": ticket_response["user_email"],
                    "responder": ticket_response["reportedby"],
                    "created_at": ticket_response["dateoccurred"],
                    "updated_at": ticket_response["id"],
                    "due_at": ticket_response["deadlinedate"],
                    # "status": ticket_response['id'],
                    "priority": ticket_response["priority"]["name"],
                    "ticket_type": "incident",  # ticket_response['tickettype']['name'],
                    "attachments": ticket_response.get("attachments", []),
                }
            ]
        }
        return zendesk_response

    def get_comment_response_mapping(self, comment_response):
        """
        Comment Mapping
        """
        zendesk_response = {
            "id": comment_response["id"],
            "note": comment_response["note"],
            "who": comment_response["who"],
        }
        return zendesk_response
