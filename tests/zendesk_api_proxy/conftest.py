import pytest


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
