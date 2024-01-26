import pytest


@pytest.fixture(scope="session")
def ess_user_request_json():
    return {"user": {"email": "somebody@example.com", "name": "Some Body"}}


@pytest.fixture(scope="session")
def ess_ticket_request_json():
    return {
        "ticket": {
            "custom_fields": [
                {"id": "31281329", "value": "export_support"},
                {"360026628958": ["andorra__ess_export"]},
                {"11977451478941": "not_exported__ess_experience"},
                {"11977507809949": "no_product_ready__ess_experience"},
                {"360026802657": "SW1A 1AA"},
                {"11977538111773": "very_positive__ess_positivity"},
                {"360026628978": "0_85000__ess_turnover_1"},
                {"360026629298": "0_10__ess_num_of_employees_1"},
                {
                    "360026629658": [
                        "advanced_engineering__ess_sector_l1",
                        "aerospace__ess_sector_l1",
                        "railways__ess_sector_l1",
                        "space__ess_sector_l1",
                    ]
                },
                {"11013312910749": "twitter__ess_acquisition"},
            ],
            "description": """Aaa Question: This is checking d-f-api.
Company Name:
Company Post Code: SW1A 1AA
Company Registration Number:
Company Turnover: Below \u00a385,000
Company Type: Private individual
Company Type Category: Sole trader or private individual
Do You Have A Product You Want To Export: No
Email: somebody@example.com
Enquiry Subject: Selling services abroad
Full Name: Some Body
Have You Exported Before: No
How Did You Hear About This Service: Twitter
Ingress Url: None
Marketing Consent: False
Markets: Andorra
Nature Of Enquiry: Wednesday! Testing again :-)
Number Of Employees: Fewer than 10
On Behalf Of: The business I own or work for (or in my own interest)
Other Sector:
Positivity For Growth: Very positive
Sectors: Advanced engineering, Aerospace, Railways, Space""",
            "requester_id": 13785027233565,
            "subject": "Wednesday! Testing again :-)",
            "submitter_id": 13785027233565,
        }
    }


ess_request_zendesk_post_json = {
    "ticket": {
        "custom_fields": [
            {"id": "31281329", "value": "export_support"},
            {"360026628958": ["andorra__ess_export"]},
            {"11977451478941": "not_exported__ess_experience"},
            {"11977507809949": "no_product_ready__ess_experience"},
            {"360026802657": "SW1A 1AA"},
            {"11977538111773": "very_positive__ess_positivity"},
            {"360026628978": "0_85000__ess_turnover_1"},
            {"360026629298": "0_10__ess_num_of_employees_1"},
            {
                "360026629658": [
                    "advanced_engineering__ess_sector_l1",
                    "aerospace__ess_sector_l1",
                    "railways__ess_sector_l1",
                    "space__ess_sector_l1",
                ]
            },
            {"11013312910749": "twitter__ess_acquisition"},
        ],
        "description": """Aaa Question: This is checking d-f-api.
Company Name:
Company Post Code: SW1A 1AA
Company Registration Number:
Company Turnover: Below \\u00a385,000
Company Type: Private individual
Company Type Category: Sole trader or private individual
Do You Have A Product You Want To Export: No
Email: nick.fitzsimons@digital.trade.gov.uk
Enquiry Subject: Selling services abroad
Full Name: Nick Fitzsimons
Have You Exported Before: No
How Did You Hear About This Service: Twitter
Ingress Url: None
Marketing Consent: False
Markets: Andorra
Nature Of Enquiry: Wednesday! Testing again :-)
Number Of Employees: Fewer than 10
On Behalf Of: The business I own or work for (or in my own interest)
Other Sector:
Positivity For Growth: Very positive
Sectors: Advanced engineering, Aerospace, Railways, Space""",
        "requester_id": 13785027233565,
        "subject": "Wednesday! Testing again :-)",
        "submitter_id": 13785027233565,
    }
}
