import json
from http import HTTPStatus

import pytest
from requests import Response

raw_halo_user_search_result = {
    "record_count": 1,
    "users": [
        {
            "id": 38,
            "name": "Some BodyFromAPI",
            "site_id": 18.0,
            "site_id_int": 18,
            "site_name": "UK Trade",
            "client_name": "Test Business Name",  # /PS-IGNORE
            "firstname": "Some",  # /PS-IGNORE
            "surname": "Body",
            "initials": "SB",
            "emailaddress": "some.bodyfromapi@example.com",  # /PS-IGNORE
            "sitephonenumber": "",
            "telpref": 0,
            "inactive": False,
            "colour": "#2bd3c6",
            "isimportantcontact": False,
            "other5": "380271314777",
            "neversendemails": False,
            "priority_id": 0,
            "linked_agent_id": 13,
            "isserviceaccount": False,
            "isimportantcontact2": False,
            "connectwiseid": 0,
            "autotaskid": -1,
            "messagegroup_id": -1,
            "sitetimezone": "",
            "use": "user",
            "client_id": 12,
            "overridepdftemplatequote": -1,
        }
    ],
}


def make_json_response(content):
    response = Response()
    response.url = "https://example.com/test"
    response.encoding = "UTF-8"
    response._content = bytes(json.dumps(content), "utf-8")
    response.headers = {"Content-Type": "application/json"}
    response.status_code = HTTPStatus.OK
    return response


raw_halo_user_search_response = make_json_response(raw_halo_user_search_result)


@pytest.fixture()
def halo_user_search_result():
    return raw_halo_user_search_result


@pytest.fixture()
def halo_user_search_response(halo_user_search_result):
    response = make_json_response(halo_user_search_result)
    return response


@pytest.fixture(scope="session")
def halo_user():
    with open("tests/other_services/directory_forms_api/fixtures/halo-user.json", "r") as fp:
        user = json.load(fp)
    return user


@pytest.fixture()
def halo_user_response(halo_user):
    return make_json_response(halo_user)


@pytest.fixture()
def halo_user_search_no_results():
    return {"record_count": 0, "users": []}
