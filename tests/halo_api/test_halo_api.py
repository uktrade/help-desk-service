import pytest
import requests
from halo.data_class import ZendeskTicket
from halo.halo_api_client import HaloAPIClient, HaloClientNotFoundException
from halo.halo_manager import HaloManager


class MockResponse:
    """
    MockResponse
    """

    def __init__(self, status_code, post_or_get):
        self.status_code = status_code
        self.post_or_get = post_or_get

    def json(self):
        if self.status_code == 200:
            if self.post_or_get == "post":
                return {"access_token": "fake-access-token"}
            else:
                return {
                    "id": 123,
                    "summary": "fake-summary",
                    "outcome": "comment",
                    "note": "The smoke is very colorful.",
                }
        else:
            return {
                "id": 123,
                "summary": "fake-summary",
                "outcome": "comment",
                "note": "The smoke is very colorful.",
            }


@pytest.fixture
def mock_response(monkeypatch):
    """Requests.get() and Requests.post() mocked to return json."""

    def wrapper(status_code, post_or_get):
        def mock_verb(*args, **kwargs):
            return MockResponse(status_code, post_or_get)

        monkeypatch.setattr(requests, post_or_get, mock_verb)

    return wrapper


class TestTicketViews:
    """
    Get Ticket and Create Ticket Tests
    """

    def test_halo_access_token_success(self, mock_response) -> None:
        """
        Token Success
        """
        mock_response(200, "post")

        result = HaloAPIClient(client_id="fake-client-id", client_secret="fake-client-secret")

        assert result.access_token == "fake-access-token"

    def test_halo_access_token_failure(self, mock_response) -> None:
        """
        Token Failure
        """
        mock_response(401, "post")
        with pytest.raises(HaloClientNotFoundException) as excinfo:
            HaloAPIClient(client_id="fake-client-id", client_secret="fake-client-secret")
        assert excinfo.typename == "HaloClientNotFoundException"

    def test_get_ticket_success(self, mock_response):
        """
        GET Ticket Success
        """
        mock_response(200, "post")

        halo_manager = HaloManager(client_id="fake-client-id", client_secret="fake-client-secret")
        mock_response(200, "get")
        ticket = halo_manager.get_ticket(123)
        assert isinstance(ticket, ZendeskTicket)
        assert ticket.summary == "fake-summary"

    def test_get_ticket_failure(self, mock_response):
        """
        GET Ticket Failure
        """
        mock_response(200, "post")

        halo_manager = HaloManager(client_id="fake-client-id", client_secret="fake-client-secret")
        mock_response(401, "get")
        with pytest.raises(HaloClientNotFoundException) as excinfo:
            halo_manager.get_ticket(123)
        assert excinfo.typename == "HaloClientNotFoundException"

    def test_post_ticket_success(self, mock_response):
        """
        POST Ticket Success
        """
        mock_response(200, "post")

        halo_manager = HaloManager(client_id="fake-client-id", client_secret="fake-client-secret")
        mock_response(201, "post")
        dummy_ticket_payload = {
            "ticket": {
                "comment": {"body": "dummy-body"},
                "priority": "urgent",
                "subject": "dummy-subject",
            }
        }
        ticket = halo_manager.create_ticket(dummy_ticket_payload)
        assert isinstance(ticket, ZendeskTicket)
        assert ticket.summary == "fake-summary"

    def test_post_ticket_failure(self, mock_response):
        """
        POST Ticket Failure
        """
        mock_response(200, "post")

        halo_manager = HaloManager(client_id="fake-client-id", client_secret="fake-client-secret")
        mock_response(401, "post")
        dummy_ticket_payload = {
            "ticket": {
                "comment": {"body": "dummy-body"},
                "priority": "urgent",
                "subject": "dummy-subject",
            }
        }
        with pytest.raises(HaloClientNotFoundException) as excinfo:
            halo_manager.create_ticket(dummy_ticket_payload)
        assert excinfo.typename == "HaloClientNotFoundException"
