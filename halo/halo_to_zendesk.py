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
                    "subject": ticket_response["summary"],
                    "id": ticket_response["id"],
                    "details": ticket_response["details"],
                    #  "user": ticket_response['id'],
                    # "group_id": ticket_response['id'],
                    # "external_id": ticket_response['id'],
                    # "assignee_id": ticket_response['user_id'],
                    "comment": ticket_response.get("comment", []),
                    "tags": ticket_response.get("tags", []),
                    # "custom_fields": ticket_response['id'],
                    # "recipient_email": ticket_response['user_email'],
                    # "responder": ticket_response['reportedby'],
                    # "created_at": ticket_response['id'],
                    # "updated_at": ticket_response['id'],
                    # "due_at": ticket_response['id'],
                    # "status": ticket_response['id'],
                    "priority": ticket_response["priority"]["name"],
                    # "ticket_type": ticket_response['id'],
                    "attachments": ticket_response.get("attachments", []),
                }
            ]
        }
        return zendesk_response
