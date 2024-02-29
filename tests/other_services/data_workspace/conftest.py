import pytest
from django.test import RequestFactory
from django.urls import reverse


@pytest.fixture()
def dataset_access_request_initial():
    return {
        "ticket": {
            "custom_fields": [
                {
                    # "id": "44394845", trust DI to have the correct values for the staging Zendesk!
                    # "value": "data_catalogue"
                    "id": "31281329",
                    "value": "data_workspace",
                }
            ],
            "description": "Access request for…",
            "id": None,
            "subject": "Access Request for Data hub source dataset testing",
            "requester": {
                "email": "somebody@example.com",  # /PS-IGNORE
                "id": None,
                "name": "Some Body",
            },
        }
    }


@pytest.fixture()
def newly_created_ticket_id():
    return 35058


@pytest.fixture()
def ticket_request_kwargs(newly_created_ticket_id):
    return {"id": newly_created_ticket_id}


@pytest.fixture()
def dataset_access_request_supplementary_private_note(newly_created_ticket_id):
    return {
        "ticket": {
            "id": newly_created_ticket_id,
            "comment": {
                "body": "Automated comment on ticket creation ",
                "id": None,
                "public": False,
            },
        }
    }


@pytest.fixture()
def halo_put_ticket_comment_request(
    rf,
    halo_creds_only,
    zendesk_authorization_header,
    dataset_access_request_supplementary_private_note,
    ticket_request_kwargs,
):
    url = reverse("api:ticket", kwargs=ticket_request_kwargs)
    request = rf.put(
        url,
        data=dataset_access_request_supplementary_private_note,
        content_type="application/json",
        HTTP_AUTHORIZATION=zendesk_authorization_header,
    )
    setattr(request, "help_desk_creds", halo_creds_only)
    return request


@pytest.fixture()
def visualisation_access_request_initial():
    return {
        "ticket": {
            "custom_fields": [{"id": "44394845", "value": "data_catalogue"}],
            "description": "An access request has been sent…",
            "id": None,
            "subject": "Data set access request received - Test Visualisation",
            "tags": ["dataset-access-request"],
            "requester": {
                "email": "somebody@example.com",  # /PS-IGNORE
                "id": None,
                "name": "Some Body",
            },
        }
    }


@pytest.fixture()
def empty_comment_for_dw_tools_access_request_body():
    return {"ticket": {"id": 35098, "comment": {"id": None, "public": False}}}


@pytest.fixture()
def empty_comment_for_dw_tools_access_request(
    zendesk_authorization_header, empty_comment_for_dw_tools_access_request_body, rf: RequestFactory
):
    url = reverse("api:tickets")
    request = rf.put(
        url,
        data=empty_comment_for_dw_tools_access_request_body,
        content_type="application/json",
        headers={"Authorization": zendesk_authorization_header},
    )
    return request
