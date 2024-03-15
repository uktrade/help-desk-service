import pytest
from email_router.ses_email_receiving.email_utils import ParsedEmail


@pytest.fixture()
def outlook_email_bytes():
    with open("tests/unit/fixtures/emails/outlook-email.txt", "rb") as file:
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
    with open("tests/unit/fixtures/emails/simple-mailbox-from-field.txt", "rb") as file:
        yield file


@pytest.fixture()
def simple_mailbox_from_email(simple_mailbox_from_email_bytes):
    return ParsedEmail(raw_bytes=simple_mailbox_from_email_bytes)
