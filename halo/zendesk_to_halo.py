class ZendeskToHalo:
    """
    This is a mapping class, where we mapp the incoming payloads to outgoing halo payloads
    """

    def create_ticket_payload(zendesk_request):
        """
        Ticket Payload
        TODO: mapping will come into picture
        """
        halo_payload = {
            "summary": zendesk_request["ticket"]["subject"],
            "details": zendesk_request.get("ticket", {}).get("description", None),
        }
        return halo_payload

    def create_comment_payload(ticket_id, zendesk_request):
        """
        Comment Payload
        TODO: mapping will come into picture
        """
        comment_payload = {
            "ticket_id": ticket_id,
            "outcome": "comment",
            "note": zendesk_request["ticket"]["comment"]["body"],
        }
        return comment_payload
