import logging
import pprint

from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from slack import WebClient


class BaseWebHook(APIView):
    """Handle Halo Events with authentication token.

    Halo will need to have a HTTP notifier and trigger configured to
    forward us comments.

    """

    def post(self, request, *args, **kwargs):
        """Handle the POSTed request from Halo.

        This will verify the shared token. If this not found or not as expected
        then 403 Forbidden will be raised.

        In all other situations the reponse 200 OK is returned. Any exceptions
        will be logged instead. This is to prevent Halo from thinking that our end
        point is broken and not sending any further events.

        """
        log = logging.getLogger(__name__)
        response = Response("OK, Thanks", status=200)

        if settings.DEBUG:
            log.debug(f"Raw POSTed data:\n{pprint.pformat(request.data)}")

        try:
            token = request.data.get("token", "<token not set in webhook request body JSON>")

            if token == settings.HALO_WEBHOOK_TOKEN:
                self.handle_event(request.data, slack_client=WebClient(), halo_client=WebClient())

            else:
                log.error(
                    "Webhook JSON body token does no match expected token "
                    "settings.HALO_WEBHOOK_TOKEN token."
                )

                if settings.DEBUG:
                    log.debug(
                        f"Webhook rejected as token '{token}' does not "
                        f"match ours '{settings.HALO_WEBHOOK_TOKEN}'"
                    )

                response = Response(status=status.HTTP_403_FORBIDDEN)

        except:  # noqa: I'm logging rather than hidding.
            # I need to respond OK or I won't receive further events.
            log.exception("Failed handling webhook because:")

        return response

    def handle_event(self, event, slack_client, halo_client):
        """Over-ridden to implement event handling.

        :param event: The POSTed dict of fields.

        :param slack_client: Slack instance to use.

        :param halo_client: Halo instance to use.

        :returns: None

        """
