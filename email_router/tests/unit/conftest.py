import json
from email import policy
from email.parser import BytesParser
from pathlib import Path

import pytest
from email_router.ses_email_receiving.email_utils import ParsedEmail
from requests import Response


@pytest.fixture(scope="function")
def email_bytes():
    fixture_path = Path(__file__).parent / "fixtures/emails/two-jpeg-attachments.email.txt"
    with open(fixture_path, "rb") as file:
        yield file


@pytest.fixture(scope="function")
def reply_to_ticket_email_bytes():
    fixture_path = Path(__file__).parent / "fixtures/emails/plain-text-reply-to-ticket-email.txt"
    with open(fixture_path, "rb") as file:
        yield file


@pytest.fixture(scope="function")
def email_message(email_bytes):
    return BytesParser(policy=policy.default).parse(email_bytes)


@pytest.fixture(scope="function")
def parsed_email(email_bytes):
    return ParsedEmail(raw_bytes=email_bytes)


@pytest.fixture(scope="function")
def parsed_reply_to_ticket_email(reply_to_ticket_email_bytes):
    return ParsedEmail(raw_bytes=reply_to_ticket_email_bytes)


@pytest.fixture(scope="session")
def zendesk_upload_request_body():
    return b"\x48\x65\x6c\x6c\x6f"


@pytest.fixture(scope="session")
def zendesk_upload_response():
    response = Response()
    response_dict = {"upload": {"token": "1234"}}
    response_json = json.dumps(response_dict)
    response._content = bytes(response_json, "utf-8")
    return response
