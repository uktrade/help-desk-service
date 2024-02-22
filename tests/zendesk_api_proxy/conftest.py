import json
from http import HTTPStatus

import pytest
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from django.test import RequestFactory
from django.urls import reverse


@pytest.fixture()
def zendesk_user_create_or_update_response_body():
    return {
        "user": {
            "id": 112233,
            "url": "https://staging-uktrade.zendesk.com/api/v2/users/112233.json",
            "name": "Some Body",
            "email": "test@example.com",  # /PS-IGNORE
            "created_at": "2023-09-25T10:09:21Z",
            "updated_at": "2024-01-29T15:11:34Z",
            "time_zone": "Amsterdam",
            "iana_time_zone": "Europe/Amsterdam",
            "phone": None,
            "shared_phone_number": None,
            "photo": None,
            "locale_id": 1,
            "locale": "en-US",
            "organization_id": None,
            "role": "admin",
            "verified": True,
            "external_id": None,
            "tags": [],
            "alias": "",
            "active": True,
            "shared": False,
            "shared_agent": False,
            "last_login_at": "2024-01-29T11:01:36Z",
            "two_factor_auth_enabled": None,
            "signature": "",
            "details": "",
            "notes": "",
            "role_type": 4,
            "custom_role_id": 360014478817,
            "moderator": True,
            "ticket_restriction": None,
            "only_private_comments": False,
            "restricted_agent": False,
            "suspended": False,
            "default_group_id": 28238069,
            "report_csv": False,
            "user_fields": {"city": None},
        }
    }


@pytest.fixture()
def zendesk_create_user_response(zendesk_user_create_or_update_response_body):
    return HttpResponse(
        json.dumps(zendesk_user_create_or_update_response_body, cls=DjangoJSONEncoder),
        headers={
            "Content-Type": "application/json",
        },
        status=HTTPStatus.CREATED,
    )


@pytest.fixture()
def zendesk_create_ticket_request(
    zendesk_authorization_header, new_zendesk_ticket_with_comment, rf: RequestFactory
):
    url = reverse("api:tickets")
    request = rf.post(
        url,
        data=new_zendesk_ticket_with_comment,
        content_type="application/json",
        headers={"Authorization": zendesk_authorization_header},
    )
    return request


@pytest.fixture()
def zendesk_create_ticket_response_body():
    # Heavily cut down
    return {
        "ticket": {
            "url": "https://staging-uktrade.zendesk.com/api/v2/tickets/35062.json",
            "id": 35062,
            "via": {"channel": "api", "source": {"from": {}, "to": {}, "rel": None}},
            "subject": "Access Request for Data hub source dataset testing",
            "raw_subject": "Access Request for Data hub source dataset testing",
            "description": "Access request for",
            "priority": None,
            "status": "new",
            "recipient": None,
            "requester_id": 13785027233565,
            "submitter_id": 13785027233565,
            "assignee_id": None,
            "organization_id": None,
            "group_id": None,
        }
    }


@pytest.fixture()
def zendesk_create_ticket_response(zendesk_create_ticket_response_body):
    return HttpResponse(
        json.dumps(zendesk_create_ticket_response_body, cls=DjangoJSONEncoder),
        headers={
            "Content-Type": "application/json",
        },
        status=HTTPStatus.CREATED,
    )
