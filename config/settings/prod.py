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


# Sentry
SENTRY_DSN = env.str("SENTRY_DSN", None)
# Configure Sentry if a DSN is set  /PS-IGNORE
if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=env.str("SENTRY_ENVIRONMENT", "Staging"),
        release=env.str("GIT_BRANCH"),
        integrations=[DjangoIntegration()],
    )
