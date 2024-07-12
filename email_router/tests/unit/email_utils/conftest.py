import json  # noqa: F401 - flake8 is complaining about imports used within fixtures
from http import HTTPStatus  # noqa: F401
from unittest import mock  # noqa: F401
from unittest.mock import Mock  # noqa: F401

import pytest
from email_router.ses_email_receiving.email_utils import (  # noqa: F401
    HaloAPIClient,
    ParsedEmail,
)
from requests import Response  # noqa: F401


@pytest.fixture()
def outlook_email_bytes():
    with open("email_router/tests/unit/fixtures/emails/outlook-email.txt", "rb") as file:
        yield file


@pytest.fixture()
def parsed_outlook_email(outlook_email_bytes):
    return ParsedEmail(raw_bytes=outlook_email_bytes)


@pytest.fixture()
def simple_mailbox_from_email_bytes():
    """
    RFC 5822 section 3.4 specifies that in a mailbox address,
    the display name is optional, having just the email address
    without angle brackets. This form of mailbox can trip up Zendesk, where
    the `requester` display name part is required,
    so this fixture has that form of mailbox in the From: field
    so that we can test our fallback for that case.
    """
    with open(
        "email_router/tests/unit/fixtures/emails/simple-mailbox-from-field.txt", "rb"
    ) as file:
        yield file


@pytest.fixture()
def simple_mailbox_from_email(simple_mailbox_from_email_bytes):
    return ParsedEmail(raw_bytes=simple_mailbox_from_email_bytes)


@pytest.fixture()
def email_sans_attachments_bytes():
    with open("email_router/tests/unit/fixtures/emails/email-sans-attachments.txt", "rb") as file:
        yield file


@pytest.fixture()
def parsed_email_sans_attachments(email_sans_attachments_bytes):
    return ParsedEmail(raw_bytes=email_sans_attachments_bytes)


@pytest.fixture()
def email_single_attachment_bytes():
    with open("email_router/tests/unit/fixtures/emails/inline-attachment-only.txt", "rb") as file:
        yield file


@pytest.fixture()
def parsed_email_single_attachment(email_single_attachment_bytes):
    return ParsedEmail(raw_bytes=email_single_attachment_bytes)


@pytest.fixture()
def plain_text_email_bytes():
    with open("email_router/tests/unit/fixtures/emails/plain-text-email.txt", "rb") as file:
        yield file


@pytest.fixture()
def parsed_plain_text_email(plain_text_email_bytes):
    return ParsedEmail(raw_bytes=plain_text_email_bytes)


@pytest.fixture()
def two_attachments_email_bytes():
    with open("email_router/tests/unit/fixtures/emails/two-attachments-email.txt", "rb") as file:
        yield file


@pytest.fixture()
def parsed_two_attachments_email(two_attachments_email_bytes):
    return ParsedEmail(raw_bytes=two_attachments_email_bytes)


@pytest.fixture()
def google_email_without_body_bytes():
    with open(
        "email_router/tests/unit/fixtures/emails/google-dmarc-email-without-body.txt", "rb"
    ) as file:
        yield file


@pytest.fixture()
def google_email_without_body(google_email_without_body_bytes):
    return ParsedEmail(raw_bytes=google_email_without_body_bytes)


@pytest.fixture()
def halo_api_client():
    halo_subdomain = "foo"
    halo_client_id = "abcdef"  # /PS-IGNORE
    halo_client_secret = "123456"
    with mock.patch(
        "email_router.ses_email_receiving.email_utils.HaloAPIClient._HaloAPIClient__authenticate"
    ) as mock_authenticate:
        mock_authenticate.return_value = "abc123"
        client = HaloAPIClient(
            halo_subdomain=halo_subdomain,
            halo_client_id=halo_client_id,
            halo_client_secret=halo_client_secret,
        )
    return client


@pytest.fixture()
def halo_create_ticket_data():
    return [
        {
            "summary": "Test Halo ticket creation",  # /PS-IGNORE
            "details": "<p>Test ticket creation</p>",
            "users_name": "Test User",  # /PS-IGNORE
            "reportedby": "test.user@example.com",  # /PS-IGNORE
            "tickettype_id": 36,
            "dont_do_rules": False,
            "customfields": [
                {"name": "CFEmailToAddress", "value": "zeta@example.com"}  # /PS-IGNORE
            ],  # /PS-IGNORE
        }
    ]


@pytest.fixture()
def halo_upload_response_content():
    with open(
        "email_router/tests/unit/fixtures/halo_responses/attachment-upload-response.json", "r"
    ) as fp:
        content = json.load(fp)
    return content


@pytest.fixture()
def halo_upload_response(halo_upload_response_content):
    response = Mock(spec=Response)
    response.json.return_value = halo_upload_response_content
    response.status_code = HTTPStatus.CREATED
    return response


@pytest.fixture()
def halo_create_ticket_response_content():
    with open(
        "email_router/tests/unit/fixtures/halo_responses/create-ticket-response.json", "r"
    ) as fp:
        content = json.load(fp)
    return content


@pytest.fixture()
def halo_create_ticket_response(halo_create_ticket_response_content):
    response = Mock(spec=Response)
    response.json.return_value = halo_create_ticket_response_content
    response.status_code = HTTPStatus.CREATED
    return response


raw_halo_user_search_result = {
    "record_count": 1,
    "users": [
        {
            "id": 38,
            "name": "Some BodyFromAPI",
            "site_id": 18.0,
            "site_id_int": 18,
            "site_name": "UK Trade",
            "client_name": "Test Business Name",  # /PS-IGNORE
            "firstname": "Some",  # /PS-IGNORE
            "surname": "Body",
            "initials": "SB",
            "emailaddress": "some.bodyfromapi@example.com",  # /PS-IGNORE
            "sitephonenumber": "",
            "telpref": 0,
            "inactive": False,
            "colour": "#2bd3c6",
            "isimportantcontact": False,
            "other5": "380271314777",
            "neversendemails": False,
            "priority_id": 0,
            "linked_agent_id": 13,
            "isserviceaccount": False,
            "isimportantcontact2": False,
            "connectwiseid": 0,
            "autotaskid": -1,
            "messagegroup_id": -1,
            "sitetimezone": "",
            "use": "user",
            "client_id": 12,
            "overridepdftemplatequote": -1,
        }
    ],
}


def make_raw_halo_user_search_response(halo_user_search_result):
    response = Response()
    response.url = "https://example.com/test"
    response.encoding = "UTF-8"
    response._content = bytes(json.dumps(halo_user_search_result), "utf-8")
    response.headers = {"Content-Type": "application/json"}
    response.status_code = HTTPStatus.OK
    return response


raw_halo_user_search_response = make_raw_halo_user_search_response(raw_halo_user_search_result)


@pytest.fixture()
def halo_user_search_result():
    return raw_halo_user_search_result


@pytest.fixture()
def halo_user_search_response(halo_user_search_result):
    response = make_raw_halo_user_search_response(halo_user_search_result)
    return response
