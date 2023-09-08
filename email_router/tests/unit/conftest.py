from email import policy
from email.parser import BytesParser
from pathlib import Path

import pytest
from email_router.ses_email_receiving.email_parser.parsed_email import ParsedEmail


@pytest.fixture(scope="session")
def email_bytes():
    fixture_path = Path(__file__).parent / "fixtures/emails/two-jpeg-attachments.email.txt"
    with open(fixture_path, "rb") as file:
        yield file


@pytest.fixture(scope="session")
def email_message(email_bytes):
    return BytesParser(policy=policy.default).parse(email_bytes)


@pytest.fixture(scope="session")
def parsed_email(email_bytes):
    return ParsedEmail(raw_bytes=email_bytes)
