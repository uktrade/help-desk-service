from halo.data_class import ZendeskComment, ZendeskTicket


class ZendeskToHalo:
    def create_ticket_payload(zendesk_request):
        halo_payload = {
            "summary": zendesk_request["ticket"]["subject"],
            "details": zendesk_request["ticket"]["description"],
        }
        return halo_payload

    def create_comment_payload(ticket_id, zendesk_request):
        comment_payload = {
            "ticket_id": ticket_id,
            "outcome": "comment",
            "note": zendesk_request["ticket"]["comment"]["body"],
        }
        return comment_payload

    def convert_halo_response_to_zendesk_comment(halo_response):
        zendesk_comment = ZendeskComment(body=halo_response["comment"]["note"])
        return zendesk_comment

    def convert_halo_response_to_zendesk_ticket(halo_response, zendesk_comment):
        zendesk_ticket = ZendeskTicket(
            subject=halo_response["summary"],
            description=halo_response["details"],
            comment=[zendesk_comment],
        )
        return zendesk_ticket
