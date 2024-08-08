import pytest
from django.http import HttpRequest
from django.test import RequestFactory
from django.urls import reverse


@pytest.fixture()
def great_feedback_form_request_body():
    return {
        "ticket": {
            "custom_fields": [{"id": "360012120972", "value": "directory"}],
            "description": "Comment: find-a-supplier form doesn't seem to be working :-/\n"
            "Email: some.body@example.com\n"  # /PS-IGNORE
            "Ingress Url: https://great.dev.uktrade.digital/\n"
            "Name: Some Body",
            "requester_id": 13785027233565,
            "subject": "Great.gov.uk contact form",
            "submitter_id": 13785027233565,
        }
    }


@pytest.fixture()
def great_domestic_ess_request_data():
    return {
        "ticket": {
            "custom_fields": [
                {"id": "360012120972", "value": "great"},
                {"17235216453277": "managing_business_risk_and_corruption_ess_dep_testing"},
            ],
            "description": "Enquiry: Test test test.\n"
            "First Name: Test\n"  # /PS-IGNORE
            "Last Name: McTest\n"  # /PS-IGNORE
            "Job Title: zxcvbnm\n"
            "Uk Telephone Number: 01514964321\n"
            "Email: some.body@example.com\n"  # /PS-IGNORE
            "Business Name: Asdfghjklqwer\n"
            "Business Type: Sole trader or private individual\n"
            "Business Postcode: SW1A 1AA\n"  # /PS-IGNORE
            "Company Registration Number: \n"
            "Type: Private individual\n"
            "Annual Turnover: Below \\u00a385,000 (Below VAT threshold)\n"  # /PS-IGNORE
            "Sector Primary: Advanced engineering\n"  # /PS-IGNORE
            "Sector Primary Other: \n"  # /PS-IGNORE
            "Sector Secondary: \n"
            "Sector Tertiary: \n"  # /PS-IGNORE
            "Product Or Service 1: Plugs\n"  # /PS-IGNORE
            "Product Or Service 2: \n"  # /PS-IGNORE
            "Product Or Service 3: \n"  # /PS-IGNORE
            "Product Or Service 4: \n"  # /PS-IGNORE
            "Product Or Service 5: \n"  # /PS-IGNORE
            "Markets: ['AF']\n"
            "Market Choices Long Form: ['Afghanistan']\n"
            "Enquiry Subject: managing_business_risk_and_corruption_ess_dep_testing\n"
            "Enquiry Subject Level 2: \n"
            "Enquiry Subject Level 3: []\n"
            "About Your Experience: I have exported before "  # /PS-IGNORE
            "but not in the last 12 months\n"  # /PS-IGNORE
            "Received Support: no\n"  # /PS-IGNORE
            "Contacted Gov Departments: no\n"  # /PS-IGNORE
            "Find Out About: twitter\n"  # /PS-IGNORE
            "Triage Journey: Cookies not accepted\n"
            "Number Of Employees: None\n"  # /PS-IGNORE
            "Ingress Url: None",  # noqa: W291
            "requester_id": 13785027233565,
            "subject": "Plugs",
            "submitter_id": 13785027233565,
        }
    }


@pytest.fixture()
def directory_forms_api_user():
    return {"user": {"email": "some.body@example.com", "name": "Some Body"}}  # /PS-IGNORE


@pytest.fixture()
def great_contact_feedback_form_ticket():
    return {
        "ticket": {
            "custom_fields": [{"id": "360012120972", "value": "great"}],
            "description": "Comment: Test 2024-07-26 15:48.\r\n\r\n"
            "Just checking what the Zendesk API call looks like.\n"
            "Email: some.body@example.com\n"  # /PS-IGNORE
            "Ingress Url: None\n"
            "Name: Some Body",
            "requester_id": 38,
            "subject": "Great.gov.uk contact form",
            "submitter_id": 38,
        }
    }


@pytest.fixture()
def great_contact_domestic_form():
    return {
        "ticket": {
            "custom_fields": [{"id": "360012120972", "value": "great"}],
            "description": "Comment: Test 2024-07-26 16:01\n"
            "Company Type: OTHER\n"
            "Company Type Other: CHARITY\n"
            "Contact Consent: ['consents_to_email_contact', 'consents_to_phone_contact']\n"
            "Email: some.body@example.com\n"  # /PS-IGNORE
            "Family Name: Body\n"
            "Given Name: Some\n"
            "Ingress Url: None\n"
            "Organisation Name: Legion of the Damned\n"
            "Postcode: SW1A 1AA",  # /PS-IGNORE
            "requester_id": 38,
            "subject": "Great.gov.uk contact form",
            "submitter_id": 38,
        }
    }


raw_great_international_contact_form_bad_service = {
    "ticket": {
        "custom_fields": [{"id": "360012120972", "value": "Great.gov.uk International"}],
        "description": "Email: some.body@example.com\n"  # /PS-IGNORE
        "Full Name: Some Body\n"
        "How We Can Help: Test 2024-07-26 16:26\n"
        "Ingress Url: None",
        "requester_id": 38,
        "subject": "Great.gov.uk International contact form",
        "submitter_id": 38,
    }
}


@pytest.fixture()
def great_international_contact_form_bad_service():
    return raw_great_international_contact_form_bad_service


@pytest.fixture()
def great_international_bad_service_dual_request(
    rf: RequestFactory,
    great_international_contact_form_bad_service,
    zendesk_and_halo_creds,
    zendesk_authorization_header,
):
    request: HttpRequest = rf.post(
        reverse("api:tickets"),
        data=great_international_contact_form_bad_service,
        content_type="application/json",
        HTTP_AUTHORIZATION=zendesk_authorization_header,
    )
    request.help_desk_creds = zendesk_and_halo_creds
    return request


@pytest.fixture()
def great_international_bad_service_halo_request(
    rf: RequestFactory,
    great_international_contact_form_bad_service,
    halo_creds_only,
    zendesk_authorization_header,
):
    request: HttpRequest = rf.post(
        reverse("api:tickets"),
        data=great_international_contact_form_bad_service,
        content_type="application/json",
        HTTP_AUTHORIZATION=zendesk_authorization_header,
    )
    request.help_desk_creds = halo_creds_only
    return request
