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
            "description": "Aaa Question: This is checking d-f-api.",
            "requester_id": 1234,
            "subject": "Wednesday! Testing again :-)",
            "submitter_id": 1234,
        }
    }


@pytest.fixture(scope="function")
def minimal_ess_ticket_request_json():
    return {
        "ticket": {
            "custom_fields": [],
            "description": "Aaa Question: This is checking d-f-api.",  # /PS-IGNORE
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
        "description": "Aaa Question: This is checking d-f-api.",  # /PS-IGNORE
        "requester_id": 13785027233565,
        "subject": "Wednesday! Testing again :-)",
        "submitter_id": 13785027233565,
    }
}


@pytest.fixture()
def ess_russia_ukraine_enquiry():
    return {
        "ticket": {
            "custom_fields": [
                {"id": "360012120972", "value": "export_support_service"},
                {"360023876777": "Test Stuff"},  # /PS-IGNORE
                {"360026747617": "SW1A 1AA"},  # /PS-IGNORE
                {
                    "1900000266233": [
                        "aerospace__ess_sector_l1",
                        "agriculture_horticulture_fisheries_and_pets__ess_sector_l1",
                    ]
                },
                {"1900000265733": "-"},
                {"11013312910749": "-"},
            ],
            "description": "Aaa Question: Test for R/U ESS form 2023-02-08 10:12",
            "requester_id": 458,
            "subject": "Russia/Ukraine Enquiry",
            "submitter_id": 458,
        }
    }


@pytest.fixture()
def ess_emergency_form_dummy_custom_fields():
    return [
        {"1900000265733": "-"},
        {"11013312910749": "-"},
    ]
