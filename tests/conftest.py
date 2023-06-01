import base64

import pytest

from help_desk_api.models import HelpDeskCreds


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass


@pytest.fixture()
def zendesk_required_settings(settings):
    settings.REQUIRE_ZENDESK = True


@pytest.fixture()
def zendesk_not_required_settings(settings):
    settings.REQUIRE_ZENDESK = False


@pytest.fixture()
def zendesk_email():
    return "test@example.com"  # /PS-IGNORE


@pytest.fixture()
def zendesk_token():
    return "ABC123"  # /PS-IGNORE


@pytest.fixture()
def client_id():
    return "client_id"  # /PS-IGNORE


@pytest.fixture()
def client_secret():
    return "client_secret"  # /PS-IGNORE


@pytest.fixture()
def zendesk_authorization_header(zendesk_email, zendesk_token):
    creds = f"{zendesk_email}/token:{zendesk_token}"
    authorization = base64.b64encode(creds.encode("ascii"))  # /PS-IGNORE
    return f"Basic {authorization.decode('ascii')}"


@pytest.fixture()
def zendesk_and_halo_creds(db, zendesk_email, zendesk_token) -> HelpDeskCreds:
    credentials = HelpDeskCreds.objects.create(
        zendesk_email=zendesk_email,
        zendesk_token=zendesk_token,
        halo_client_id="test_halo_client_id",
        halo_client_secret="test_halo_client_secret",
        help_desk=[
            HelpDeskCreds.HelpDeskChoices.ZENDESK,
            HelpDeskCreds.HelpDeskChoices.HALO,
        ],
    )
    credentials.set_token()
    credentials.save()
    return credentials


@pytest.fixture()
def halo_creds_only(db, zendesk_email, zendesk_token) -> HelpDeskCreds:
    credentials = HelpDeskCreds.objects.create(
        zendesk_email=zendesk_email,
        # TODO: what about a new service with no Zendesk token?
        # TODO: Is this really the same as the actual Zendesk token?
        zendesk_token=zendesk_token,
        halo_client_id="test_halo_client_id",
        halo_client_secret="test_halo_client_secret",
        help_desk=[
            HelpDeskCreds.HelpDeskChoices.HALO,
        ],
    )
    credentials.set_token()
    credentials.save()
    return credentials


@pytest.fixture()
def zendesk_creds_only(db, zendesk_email, zendesk_token) -> HelpDeskCreds:
    credentials = HelpDeskCreds.objects.create(
        zendesk_email=zendesk_email,
        zendesk_token=zendesk_token,
        help_desk=[
            HelpDeskCreds.HelpDeskChoices.ZENDESK,
        ],
    )
    credentials.set_token()
    credentials.save()
    return credentials
