import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

from config.settings.base import *  # type: ignore # noqa

sentry_sdk.init(
    os.environ.get("SENTRY_DSN"),
    environment=os.environ.get("SENTRY_ENVIRONMENT"),
    integrations=[DjangoIntegration()],
)
