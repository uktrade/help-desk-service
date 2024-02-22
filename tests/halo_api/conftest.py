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


@pytest.fixture()
def ess_zendesk_ticket_request_body():
    return {
        "ticket": {
            "custom_fields": [
                {"id": "360012120972", "value": "export_support_service"},
                {"11977451478941": "more_than_a_year_ago__ess_experience"},
                {"360026747617": "SW1A 1AA"},  # /PS-IGNORE
                {"11977538111773": "neutral__ess_positivity"},
                {"1900000266173": "0_85000__ess_turnover_1"},
                {"360023852217": "0_10__ess_num_of_employees_1"},
                {
                    "1900000266233": [
                        "aerospace__ess_sector_l1",
                        "space__ess_sector_l1",
                        "technology_and_smart_cities__ess_sector_l1",
                    ]
                },
                {"11013312910749": "twitter__ess_acquisition"},
            ],
            "description": """Aaa Question: Yet another attempt
Company Name:
Company Post Code: SW1A 1AA /PS-IGNORE
Company Registration Number:
Company Turnover: Below \\u00a385,000
Company Type: Private individual
Company Type Category: Sole trader or private individual
Do You Have A Product You Want To Export:
Email: somebody@example.com /PS-IGNORE
Enquiry Subject: Selling goods abroad
Full Name: Some Body
Have You Exported Before: Yes, more than a year ago
How Did You Hear About This Service: Twitter
Ingress Url: None
Marketing Consent: False
Markets: Andorra, Iceland
Nature Of Enquiry: Test 2024-02-06 10:04
Number Of Employees: Fewer than 10
On Behalf Of: The business I own or work for (or in my own interest)
Other Sector:
Positivity For Growth: Neutral
Sectors: Aerospace, Space, Technology and smart cities""",  # /PS-IGNORE
            "requester_id": 13785027233565,
            "subject": "Test 2024-02-06 10:04",
            "submitter_id": 13785027233565,
        }
    }


@pytest.fixture()
def private_ticket_comment():
    return {
        "ticket": {
            "id": 123,
            "comment": {
                "body": "A comment",
                "id": None,
                "public": False,
            },
        }
    }


@pytest.fixture()
def public_ticket_comment():
    return {
        "ticket": {
            "id": 123,
            "comment": {
                "body": "A comment",
                "id": None,
                "public": True,
            },
        }
    }
