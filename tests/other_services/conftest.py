import pytest


@pytest.fixture(scope="session")
def datahub_frontend_support_ticket():
    return {
        "ticket": {
            "requester": {"name": "Data Hub user", "email": "foo@bar.baz"},  # /PS-IGNORE
            "subject": "Test 2023-12-06 11:40",
            "comment": {"body": "Blah"},
            "custom_fields": [
                {"id": "34146805", "value": "Safari 16.3, Macos 10.15.7"},  # /PS-IGNORE
                {"id": "31281329", "value": "datahub"},
            ],
            "tags": ["feedback"],
        }
    }
