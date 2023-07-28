import logging

from halo.data_class import ZendeskException
from halo.halo_manager import HaloManager
from halo.message_tools import messages_for_slack
from halo.slack_api import post_message


def comments_from_halo(event, slack_client, halo_client):
    """Handle the raw event from a Halo webhook and return without error.

    This will log all exceptions rather than cause halo reject
    our endpoint.

    """
    log = logging.getLogger(__name__)

    chat_id = event["chat_id"]
    ticket_id = event["ticket_id"]
    if not chat_id:
        log.debug("chat_id is empty, ignoring ticket comment.")
        return []

    log.debug(f"Recovering ticket by its Halo ID:<{ticket_id}>")
    try:
        issue = HaloManager.get_ticket(chat_id, ticket_id)  # TODO: chat_id??

    except ZendeskException:
        log.debug(f"chat_id:<{chat_id}> not found, ignoring ticket comment.")
        return []

    # Recover all messages from the slack conversation:
    resp = slack_client.conversations_replies(channel=issue.channel_id, ts=chat_id)
    slack = [message for message in resp.data["messages"]]

    # Recover all comments on this ticket:
    halo = [comment.to_dict() for comment in halo_client.tickets.comments(ticket=ticket_id)]

    # Work out what needs to be posted to slack:
    for_slack = messages_for_slack(slack, halo)

    # Update the slack conversation:
    for message in for_slack:
        msg = f"(Halo): {message['body']}"
        post_message(slack_client, chat_id, issue.channel_id, msg)

    return for_slack
