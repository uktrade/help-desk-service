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
def halo_creds_only(
    db, zendesk_not_required_settings, zendesk_email, zendesk_token
) -> HelpDeskCreds:
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
        zendesk_subdomain="abc123",
        help_desk=[
            HelpDeskCreds.HelpDeskChoices.ZENDESK,
        ],
    )
    credentials.set_token()
    credentials.save()
    return credentials


@pytest.fixture(scope="session")
def new_zendesk_ticket():
    """
    This is an example of the ticket submission for a
    new dataset request
    on Data Workspace  /PS-IGNORE
    """
    return {
        "description": "Long load of text here",
        "subject": "Request for new dataset on Data Workspace",  # /PS-IGNORE
        "tags": ["request-for-data"],
    }


@pytest.fixture(scope="session")
def new_zendesk_ticket_with_comment_attachments():
    """
    This is an example of the ticket submission for a
    new dataset request
    on Data Workspace  /PS-IGNORE
    """
    return {
        "ticket": {
            "comment": {
                "body": "Initial comment is the way descriptions ought to be added",
                "attachments": [7, 14, 21],
            },
            "subject": "Test for attachments",  # /PS-IGNORE
        }
    }


@pytest.fixture(scope="session")
def new_halo_ticket():
    """
    This is an example of a much-abbreviated Halo response on ticket creation
    """
    return {
        "id": 1234,
        "dateoccurred": "2023-06-29T10:16:08.8378294Z",
        "summary": "Request for new dataset on Data Workspace",  # /PS-IGNORE
        "details": "Long load of text here",
        "user_id": 0,
        "deadlinedate": "1900-01-01T00:00:00",
        "tags": [
            {"id": 0, "text": "first"},
            {"id": 0, "text": "second"},
            {"id": 0, "text": "third tag"},
        ],
        "user": {"id": 1, "name": "test", "emailaddress": "test@test.co"},  # /PS-IGNORE
        "actions": [{"id": 2, "outcome": "comment", "note": "test"}],
        "attachments": [
            {"id": 7, "filename": "a", "isimage": True},
            {"id": 14, "filename": "b", "isimage": True},
            {"id": 21, "filename": "c", "isimage": True},
        ],
    }


@pytest.fixture(scope="session")
def access_token():
    return {"access_token": "fake-access-token"}  # /PS-IGNORE


@pytest.fixture(scope="session")
def attachment_filename():
    return "test_filename.dat"


@pytest.fixture(scope="session")
def attachment_data():
    return "Some string".encode("utf-8")


@pytest.fixture(scope="session")
def halo_upload_response_body():
    return {
        "third_party_id": "",
        "content_type": "image/jpeg",
        "id": 218,
        "filename": "padana-2.jpg",
        "datecreated": "2023-09-15T11:11:37.9383455Z",
        "note": "",
        "filesize": 84061,
        "type": 0,
        "unique_id": 0,
        "desc": "padana-2.jpg",
        "isimage": False,
        "data": "/9j/4AAQSk",
    }
