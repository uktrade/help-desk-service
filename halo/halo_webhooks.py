from halo.base_webhook import BaseWebHook
from halo.halo_to_slack import comments_from_halo


class CommentsWebHook(BaseWebHook):
    """Handle Halo Comment Events."""

    def handle_event(self, event, slack_client, halo_client):
        """Handle the comment trigger event we have been POSTed.

        Recover and update the comments with lastest from Halo.

        """
        comments_from_halo(event, slack_client, halo_client)
