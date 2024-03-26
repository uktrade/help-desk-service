import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from config.settings.base import *  # type: ignore # noqa


def strip_handled_exceptions(event, _hint):
    # Ignore logged errors
    if "logger" in event:
        return None

    # Ignore handled exceptions
    exceptions = event.get("exception", {}).get("values", [])
    if exceptions:
        exc = exceptions[-1]
        mechanism = exc.get("mechanism")

        if mechanism:
            if mechanism.get("handled"):
                return None

    return event


sentry_sdk.init(
    os.environ.get("SENTRY_DSN"),
    environment=os.environ.get("SENTRY_ENVIRONMENT"),
    integrations=[DjangoIntegration()],
    # before_send=strip_handled_exceptions,
)
