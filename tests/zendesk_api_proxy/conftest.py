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
            "tags": ["request-for-data"],
        },
        "audit": {},
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


@pytest.fixture()
def halo_create_ticket_response_body():
    return {
        "ticket": {
            "id": 3265,
            "subject": "Request for new dataset on Data Workspace",
            "description": "<p>A request for a new dataset on Data Workspace",
            "user": {
                "id": 38,
                "name": "Some Body",
                "email": "somebody@example.com",  # /PS-IGNORE
            },
            "group_id": 18,
            "tags": ["request-for-data"],
            "recipient": "",
            "created_at": "2024-02-22T16:11:34.4560052Z",
            "updated_at": "2024-02-22T16:11:44.896963Z",
            "due_at": "2024-02-29T16:11:34.4560052Z",
            "status": "new",
            "priority": "low",
            "assignee_id": 1,
        },
        "audit": {},
    }


@pytest.fixture()
def halo_create_ticket_response(halo_create_ticket_response_body):
    return HttpResponse(
        json.dumps(halo_create_ticket_response_body, cls=DjangoJSONEncoder),
        headers={
            "Content-Type": "application/json",
        },
        status=HTTPStatus.CREATED,
    )


@pytest.fixture()
def another_zendesk_create_ticket_response_body():
    return {
        "ticket": {
            "url": "https://staging-uktrade.zendesk.com/api/v2/tickets/35087.json",
            "id": 35087,
            "external_id": None,
            "via": {"channel": "api", "source": {"from": {}, "to": {}, "rel": None}},
            "created_at": "2024-02-22T16:11:34Z",
            "updated_at": "2024-02-22T16:11:34Z",
            "type": None,
            "subject": "Request for new dataset on Data Workspace",
            "raw_subject": "Request for new dataset on Data Workspace",
            "description": "\nA request for a new dataset on Data Workspace",
            "priority": None,
            "status": "new",
            "recipient": None,
            "requester_id": 13785027233565,
            "submitter_id": 13785027233565,
            "assignee_id": None,
            "organization_id": None,
            "group_id": None,
            "collaborator_ids": [],
            "follower_ids": [],
            "email_cc_ids": [],
            "forum_topic_id": None,
            "problem_id": None,
            "has_incidents": False,
            "is_public": True,
            "due_at": None,
            "tags": ["data_catalogue", "request-for-data"],
            "custom_fields": [
                {"id": 44394765, "value": False},
                {"id": 360026629658, "value": None},
                {"id": 44394785, "value": None},
                {"id": 44379689, "value": None},
                {"id": 44394805, "value": None},
                {"id": 360028508078, "value": None},
                {"id": 44394825, "value": False},
                {"id": 44394845, "value": "data_catalogue"},
                {"id": 360026628958, "value": None},
                {"id": 44394605, "value": None},
                {"id": 360026628978, "value": None},
                {"id": 1900002239093, "value": None},
                {"id": 360026629298, "value": None},
                {"id": 360026802637, "value": None},
                {"id": 360026802657, "value": None},
                {"id": 44380149, "value": None},
                {"id": 4414309789329, "value": None},
            ],
            "satisfaction_rating": None,
            "sharing_agreement_ids": [],
            "custom_status_id": 1900002051893,
            "fields": [
                {"id": 44394765, "value": False},
                {"id": 360026629658, "value": None},
                {"id": 44394785, "value": None},
                {"id": 44379689, "value": None},
                {"id": 44394805, "value": None},
                {"id": 360028508078, "value": None},
                {"id": 44394825, "value": False},
                {"id": 44394845, "value": "data_catalogue"},
                {"id": 360026628958, "value": None},
                {"id": 44394605, "value": None},
                {"id": 360026628978, "value": None},
                {"id": 1900002239093, "value": None},
                {"id": 360026629298, "value": None},
                {"id": 360026802637, "value": None},
                {"id": 360026802657, "value": None},
                {"id": 44380149, "value": None},
                {"id": 4414309789329, "value": None},
            ],
            "followup_ids": [],
            "brand_id": 3155849,
            "allow_channelback": False,
            "allow_attachments": True,
            "from_messaging_channel": False,
        },
        "audit": {
            "id": 16960233275933,
            "ticket_id": 35087,
            "created_at": "2024-02-22T16:11:34Z",
            "author_id": 10361731669,
            "metadata": {
                "system": {
                    "client": "python-requests/2.31.0",
                    "ip_address": "18.130.41.69",
                    "location": "London, ENG, United Kingdom",  # /PS-IGNORE
                    "latitude": 51.5088,
                    "longitude": -0.093,
                },
                "custom": {},
                "flags": [11],
                "flags_options": {
                    "11": {
                        "message": {"user": "DIT Staging", "user_id": 10361731669},
                        "trusted": False,
                    }
                },
                "trusted": False,
            },
            "events": [
                {
                    "id": 16960233276061,
                    "type": "Comment",
                    "author_id": 13785027233565,
                    "body": "A request for a new dataset",
                    "html_body": '<div class="zd-comment" dir="auto">'
                    '<p dir="auto">A request for a new dataset</p>',
                    "plain_body": "A request for a new dataset",
                    "public": True,
                    "attachments": [],
                    "audit_id": 16960233275933,
                },
                {
                    "id": 16960233276189,
                    "type": "Create",
                    "value": "13785027233565",
                    "field_name": "requester_id",
                },
                {
                    "id": 16960233276317,
                    "type": "Create",
                    "value": "Request for new dataset on Data Workspace",
                    "field_name": "subject",
                },
                {
                    "id": 16960233276445,
                    "type": "Create",
                    "value": ["data_catalogue", "request-for-data"],
                    "field_name": "tags",
                },
                {
                    "id": 16960233276573,
                    "type": "Create",
                    "value": "data_catalogue",
                    "field_name": "44394845",
                },
                {"id": 16960233276701, "type": "Create", "value": None, "field_name": "priority"},
                {"id": 16960233276829, "type": "Create", "value": None, "field_name": "type"},
                {"id": 16960233276957, "type": "Create", "value": "new", "field_name": "status"},
                {
                    "id": 16960233277085,
                    "type": "Create",
                    "value": "8872077832733",
                    "field_name": "ticket_form_id",
                },
                {
                    "id": 16960233277213,
                    "type": "Notification",
                    "via": {
                        "channel": "rule",
                        "source": {
                            "from": {
                                "deleted": False,
                                "title": "Data Workspace - notify user",  # /PS-IGNORE
                                "id": 360057683258,
                            },
                            "rel": "trigger",
                        },
                    },
                    "subject": "Data Workspace data request",
                    "body": "The Data Workspace team has received",
                    "recipients": [13785027233565],
                },
            ],
            "via": {"channel": "api", "source": {"from": {}, "to": {}, "rel": None}},
        },
    }
