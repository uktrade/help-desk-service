import pytest


@pytest.fixture()
def dataset_access_request_initial():
    return {
        "ticket": {
            "custom_fields": [
                {
                    # "id": "44394845", trust DI to have the correct values for the staging Zendesk!
                    # "value": "data_catalogue"
                    "id": "31281329",
                    "value": "data_workspace",
                }
            ],
            "description": "Access request for…",
            "id": None,
            "subject": "Access Request for Data hub source dataset testing",
            "requester": {
                "email": "somebody@example.com",  # /PS-IGNORE
                "id": None,
                "name": "Some Body",
            },
        }
    }


@pytest.fixture()
def visualisation_access_request_initial():
    return {
        "ticket": {
            "custom_fields": [{"id": "44394845", "value": "data_catalogue"}],
            "description": "An access request has been sent…",
            "id": None,
            "subject": "Data set access request received - Test Visualisation",
            "tags": ["dataset-access-request"],
            "requester": {
                "email": "somebody@example.com",  # /PS-IGNORE
                "id": None,
                "name": "Some Body",
            },
        }
    }
