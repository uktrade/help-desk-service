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
        zendesk_subdomain="staging-uktrade",
        help_desk=[
            HelpDeskCreds.HelpDeskChoices.ZENDESK,
        ],
    )
    credentials.set_token()
    credentials.save()
    return credentials


@pytest.fixture(scope="function")
def zendesk_ticket_subject_and_comment_only():
    return {
        "comment": {
            "body": "Long load of text here",
        },
        "subject": "Request for new dataset on Data Workspace",  # /PS-IGNORE
    }


@pytest.fixture(scope="function")
def new_zendesk_ticket_with_description():
    """
    This is an example of the ticket submission for a
    new dataset request
    on Data Workspace  /PS-IGNORE
    """
    return {
        "description": "Long load of text here",
        "subject": "Request for new dataset on Data Workspace",  # /PS-IGNORE
        "tags": ["request-for-data"],
        "recipient": "someone@example.gov.uk",  # /PS-IGNORE
        "custom_fields": [
            {"id": 44394765, "value": False},
            {
                "id": 360026629658,
                "value": None,
            },
            {"id": 31281329, "value": "data_workspace"},
        ],
    }


@pytest.fixture(scope="function")
def new_zendesk_ticket_with_comment():
    """
    This is an example of the ticket submission for a
    new dataset request
    on Data Workspace  /PS-IGNORE
    """
    return {
        "comment": {
            "body": "Long load of text here",
        },
        "subject": "Request for new dataset on Data Workspace",  # /PS-IGNORE
        "tags": [
            "request-for-data",
            "another-tag",
        ],
        "recipient": "someone@example.gov.uk",  # /PS-IGNORE
        "custom_fields": [
            {"id": 44394765, "value": False},
            {
                "id": 360026629658,
                "value": None,
            },
            {"id": 31281329, "value": "data_workspace"},
        ],
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
        "agent_id": 123,
        "team_id": 1,
        "deadlinedate": "1900-01-01T00:00:00",
        "tags": [{"id": 0, "text": "data-workspace"}, {"id": 0, "text": "access-request"}],
        "user": {"id": 1, "name": "test", "emailaddress": "test@test.co"},  # /PS-IGNORE
        "attachments": [
            {"id": 7, "filename": "a", "isimage": True},
            {"id": 14, "filename": "b", "isimage": True},
            {"id": 21, "filename": "c", "isimage": True},
        ],
        "customfields": [
            {
                "id": 213,
                "name": "CFEmailToAddress",
                "label": "Request sent to email address",
                "summary": "",
                "type": 0,
                "value": "datahub@support.businessandtrade.gov.uk",  # /PS-IGNORE
                "display": "datahub@support.businessandtrade.gov.uk",  # /PS-IGNORE
                "characterlimit": 0,
                "characterlimittype": 0,
                "inputtype": 0,
                "copytochild": False,
                "searchable": False,
                "ordervalues": True,
                "ordervaluesby": 0,
                "database_lookup_auto": False,
                "extratype": 0,
                "copytochildonupdate": False,
                "usage": 1,
                "showondetailsscreen": False,
                "custom_extra_table_id": 0,
                "copytorelated": False,
                "calculation": "",
                "regex": "",
                "is_horizontal": False,
                "isencrypted": False,
                "selection_field_id": 0,
            },
            {
                "id": 175,
                "name": "CFChangeActualEndDateTime",  # /PS-IGNORE
                "label": "Actual End Date/Time ",
                "summary": "",
                "type": 4,
                "value": "2023-11-09T15:48:38.2790589Z",
                "display": "09/11/2023",
                "characterlimit": 0,
                "characterlimittype": 0,
                "inputtype": 1,
                "copytochild": False,
                "searchable": False,
                "ordervalues": True,
                "ordervaluesby": 1,
                "database_lookup_auto": False,
                "extratype": 0,
                "copytochildonupdate": False,
                "usage": 1,
                "showondetailsscreen": False,
                "custom_extra_table_id": 0,
                "copytorelated": False,
                "calculation": "",
                "regex": "",
                "is_horizontal": False,
                "isencrypted": False,
                "selection_field_id": 0,
            },
            {
                "id": 174,
                "name": "CFChangeActualStartDateTime",
                "label": "Actual Start Date/Time",
                "summary": "",
                "type": 4,
                "value": "2023-11-09T15:48:38.2790628Z",
                "display": "09/11/2023",
                "characterlimit": 0,
                "characterlimittype": 0,
                "inputtype": 1,
                "copytochild": False,
                "searchable": False,
                "ordervalues": True,
                "ordervaluesby": 1,
                "database_lookup_auto": False,
                "extratype": 0,
                "copytochildonupdate": False,
                "usage": 1,
                "showondetailsscreen": False,
                "custom_extra_table_id": 0,
                "copytorelated": False,
                "calculation": "",
                "regex": "",
                "is_horizontal": False,
                "isencrypted": False,
                "selection_field_id": 0,
            },
            {
                "id": 113,
                "name": "CFdesktopType",
                "label": "Desktop Type",
                "summary": "",
                "type": 2,
                "value": "1",
                "display": "Standard Desktop",
                "characterlimit": 0,
                "characterlimittype": 0,
                "inputtype": 0,
                "copytochild": True,
                "searchable": True,
                "ordervalues": False,
                "ordervaluesby": 0,
                "database_lookup_auto": False,
                "third_party_name": "",
                "extratype": 1,
                "copytochildonupdate": False,
                "hyperlink": "",
                "usage": 1,
                "showondetailsscreen": False,
                "custom_extra_table_id": 0,
                "copytorelated": False,
                "calculation": "",
                "regex": "",
                "is_horizontal": False,
                "isencrypted": False,
                "selection_field_id": 0,
            },
            {
                "id": 124,
                "name": "CFlaptopType",
                "label": "Laptop Type",
                "summary": "",
                "type": 2,
                "value": "1",
                "display": "Standard Laptop",  # /PS-IGNORE
                "characterlimit": 0,
                "characterlimittype": 0,
                "inputtype": 0,
                "copytochild": True,
                "searchable": True,
                "ordervalues": False,
                "ordervaluesby": 0,
                "database_lookup_auto": False,
                "third_party_name": "",
                "extratype": 1,
                "copytochildonupdate": False,
                "hyperlink": "",
                "usage": 1,
                "showondetailsscreen": False,
                "custom_extra_table_id": 0,
                "copytorelated": False,
                "calculation": "",
                "regex": "",
                "is_horizontal": False,
                "isencrypted": False,
                "selection_field_id": 0,
            },
            {
                "id": 132,
                "name": "CFprinterRequestType",
                "label": "Printer Request Type",
                "summary": "",
                "type": 2,
                "value": "1",
                "display": "New",
                "characterlimit": 0,
                "characterlimittype": 0,
                "inputtype": 0,
                "copytochild": True,
                "searchable": True,
                "ordervalues": False,
                "ordervaluesby": 0,
                "database_lookup_auto": False,
                "third_party_name": "",
                "copytochildonupdate": False,
                "hyperlink": "",
                "usage": 1,
                "showondetailsscreen": False,
                "custom_extra_table_id": 0,
                "copytorelated": False,
                "calculation": "",
                "regex": "",
                "is_horizontal": False,
                "isencrypted": False,
                "selection_field_id": 0,
            },
            {
                "id": 206,
                "name": "CFService",  # /PS-IGNORE
                "label": "Service",
                "summary": "",
                "type": 2,
                "value": 9,
                "display": "Datahub",
                "characterlimit": 0,
                "characterlimittype": 0,
                "inputtype": 0,
                "copytochild": False,
                "searchable": False,
                "ordervalues": True,
                "ordervaluesby": 0,
                "database_lookup_auto": False,
                "extratype": 1,
                "copytochildonupdate": False,
                "usage": 1,
                "showondetailsscreen": False,
                "custom_extra_table_id": 0,
                "copytorelated": False,
                "calculation": "",
                "regex": "",
                "is_horizontal": False,
                "isencrypted": False,
                "selection_field_id": 0,
            },
        ],
        "fixbydate": "2023-11-16T15:48:37.2094386Z",
        "lastactiondate": "2023-11-09T15:48:39.5816272Z",
        "priority_id": 4,
        "priority": {
            "name": "Low",
        },
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


@pytest.fixture()
def zendesk_user_get_or_create_response():
    return {"user": {"email": "someone@example.com", "name": "Some One"}}  # /PS-IGNORE
