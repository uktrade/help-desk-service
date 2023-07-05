class ZendeskToHalo:
    """
    This is a mapping class, where we map the incoming payloads to outgoing halo payloads
    """

    def create_ticket_payload(self, zendesk_request):
        """
        Ticket Payload
        TODO: map all the fields, atm it is subset
        """
        halo_payload = {
            "summary": zendesk_request.get("ticket", {}).get("subject", None),
            "details": zendesk_request.get("ticket", {}).get("description", None),
        }
        return halo_payload

    def create_comment_payload(self, ticket_id, zendesk_request):
        """
        Comment Create Payload
        TODO: mapping will come into picture
        """
        comment_payload = {
            "ticket_id": ticket_id,
            "outcome": "comment",
            "note": zendesk_request["ticket"]["comment"]["body"],
        }
        return comment_payload

    def update_comment_payload(self, zendesk_request):
        """
        Comment Update Payload
        TODO: mapping will come into picture
        """
        if "id" in zendesk_request["ticket"]["comment"]:
            comment_payload = {
                "ticket_id": zendesk_request["id"],
                "id": zendesk_request["ticket"]["comment"]["id"],
                "outcome": "comment",
                "note": zendesk_request["ticket"]["comment"]["body"],
            }
        else:
            comment_payload = self.create_comment_payload(zendesk_request["id"], zendesk_request)
        return comment_payload