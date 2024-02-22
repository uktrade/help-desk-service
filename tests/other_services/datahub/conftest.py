import pytest

from help_desk_api.models import HelpDeskCreds


@pytest.fixture(scope="function")
def datahub_frontend_support_ticket():
    return {
        "ticket": {
            "requester": {"name": "Data Hub user", "email": "somebody@example.com"},  # /PS-IGNORE
            "subject": "Test 2023-12-06 11:40",
            "comment": {"body": "Blah"},
            "custom_fields": [
                {"id": "34146805", "value": "Safari 16.3, Macos 10.15.7"},  # /PS-IGNORE
                {"id": "31281329", "value": "datahub"},
            ],
            "tags": ["feedback"],
        }
    }


@pytest.fixture()
def datahub_zendesk_creds_only(db) -> HelpDeskCreds:
    credentials = HelpDeskCreds.objects.create(
        zendesk_email="tools@digital.trade.gov.uk",  # zendesk_email, /PS-IGNORE
        zendesk_token="a-zendesk-token",  # zendesk_token
        zendesk_subdomain="staging-uktrade",
        help_desk=[
            HelpDeskCreds.HelpDeskChoices.ZENDESK,
        ],
    )
    credentials.set_token()
    credentials.save()
    return credentials
