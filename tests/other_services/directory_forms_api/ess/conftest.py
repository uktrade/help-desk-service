import pytest


@pytest.fixture(scope="function")
def ess_user_request_json():
    return {"user": {"email": "somebody@example.com", "name": "Some Body"}}  # /PS-IGNORE


@pytest.fixture(scope="function")
def ess_ticket_request_json():
    return {
        "ticket": {
            "custom_fields": [
                {"id": "360012120972", "value": "export_support_service"},
                {"11977451478941": "in_the_last_year__ess_experience"},
                {"360023876777": "Bananas Inc."},  # /PS-IGNORE
                {"360026747617": "SW1A 1AA"},  # /PS-IGNORE
                {"11977538111773": "very_positive__ess_positivity"},
                {"1900000265733": "partnership__ess_organistation"},
                {"1900000266173": "50000000__ess_turnover_1"},
                {"360023852217": "0_10__ess_num_of_employees_1"},
                {
                    "1900000266233": [
                        "aerospace__ess_sector_l1",
                        "railways__ess_sector_l1",
                        "space__ess_sector_l1",
                    ]
                },
                {"11013312910749": "radio_advert__ess_acquisition"},
            ],
            "description": "Aaa Question: This is checking d-f-api.\n"
            "Company Name:\n"
            "|Company Post Code: SW1A 1AA:\n"  # /PS-IGNORE
            "Company Registration Number::\n"
            "Company Turnover: Below \u00a385,000:\n"
            "Company Type: Private individual:\n"
            "Company Type Category: Sole trader or private individual:\n"
            "Do You Have A Product You Want To Export: No:\n"  # /PS-IGNORE
            "Email: somebody@example.com:\n"  # /PS-IGNORE
            "Enquiry Subject: Selling services abroad:\n"  # /PS-IGNORE
            "Full Name: Some Body:\n"
            "Have You Exported Before: No:\n"  # /PS-IGNORE
            "How Did You Hear About This Service: Twitter:\n"
            "Ingress Url: None:\n"
            "Marketing Consent: False:\n"  # /PS-IGNORE
            "Markets: Andorra:\n"
            "Nature Of Enquiry: Wednesday! Testing again :-):\n"  # /PS-IGNORE
            "Number Of Employees: Fewer than 10:\n"  # /PS-IGNORE
            "On Behalf Of: The business I own or work for (or in my own interest):\n"  # /PS-IGNORE
            "Other Sector::\n"
            "Positivity For Growth: Very positive:\n"  # /PS-IGNORE
            "Sectors: Advanced engineering, Aerospace, Railways, Space",  # /PS-IGNORE
            "requester_id": 13785027233565,
            "subject": "Wednesday! Testing again :-)",
            "submitter_id": 13785027233565,
        }
    }


ess_request_zendesk_post_json = {
    "ticket": {
        "custom_fields": [
            {"id": "31281329", "value": "export_support"},
            {"360026628958": ["andorra__ess_export"]},  # /PS-IGNORE
            {"11977451478941": "not_exported__ess_experience"},
            {"11977507809949": "no_product_ready__ess_experience"},
            {"360026802657": "SW1A 1AA"},  # /PS-IGNORE
            {"11977538111773": "very_positive__ess_positivity"},
            {"360026628978": "0_85000__ess_turnover_1"},
            {"360026629298": "0_10__ess_num_of_employees_1"},
            {
                "360026629658": [  # /PS-IGNORE
                    "advanced_engineering__ess_sector_l1",
                    "aerospace__ess_sector_l1",
                    "railways__ess_sector_l1",
                    "space__ess_sector_l1",
                ]
            },
            {"11013312910749": "twitter__ess_acquisition"},
        ],
        "description": "Aaa Question: This is checking d-f-api.\n"
        "Company Name:\n"
        "Company Post Code: SW1A 1AA\n"  # /PS-IGNORE
        "Company Registration Number:\n"
        "Company Turnover: Below \\u00a385,000\n"
        "Company Type: Private individual\n"
        "Company Type Category: Sole trader or private individual\n"
        "Do You Have A Product You Want To Export: No\n"  # /PS-IGNORE
        "Email: somebody@example.com\n"  # /PS-IGNORE
        "Enquiry Subject: Selling services abroad\n"  # /PS-IGNORE
        "Full Name: Some Body\n"
        "Have You Exported Before: No\n"  # /PS-IGNORE
        "How Did You Hear About This Service: Twitter\n"
        "Ingress Url: None\n"
        "Marketing Consent: False\n"  # /PS-IGNORE
        "Markets: Andorra\n"
        "Nature Of Enquiry: Wednesday! Testing again :-)\n"  # /PS-IGNORE
        "Number Of Employees: Fewer than 10\n"  # /PS-IGNORE
        "On Behalf Of: The business I own or work for (or in my own interest)\n"  # /PS-IGNORE
        "Other Sector:\n"
        "Positivity For Growth: Very positive\n"  # /PS-IGNORE
        "Sectors: Advanced engineering, Aerospace, Railways, Space",  # /PS-IGNORE
        "requester_id": 13785027233565,
        "subject": "Wednesday! Testing again :-)",
        "submitter_id": 13785027233565,
    }
}
