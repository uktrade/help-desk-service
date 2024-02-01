import pytest


@pytest.fixture()
def ticket_request_with_suitable_requester():
    return {
        "requester": {"name": "Some Body", "email": "somebody@example.com"},  # /PS-IGNORE
        "subject": "Test 2023-12-06 11:40",
        "comment": {"body": "Blah"},
        "requester_id": 13785027233565,
        "submitter_id": 13785027233565,
    }


@pytest.fixture()
def ticket_request_with_requester_id():
    return {
        "subject": "Test 2023-12-06 11:40",
        "comment": {"body": "Blah"},
        "requester_id": 13785027233565,
        "submitter_id": 13785027233565,
    }


@pytest.fixture()
def ticket_request_lacking_any_requester():
    return {
        "subject": "Test 2023-12-06 11:40",
        "comment": {"body": "Blah"},
    }
