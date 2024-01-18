import re
from http import HTTPStatus
from unittest import mock
from xml.etree import ElementTree as ET

from django.urls import reverse
from healthcheck.views import HealthCheckView


def raise_exception():
    raise Exception()


class TestHealthCheckStatus:
    @mock.patch("healthcheck.views.HelpDeskCreds")
    def test_status_ok(self, mock_help_desk_creds):
        view = HealthCheckView()

        status = view.get_status_code()

        assert status == HTTPStatus.OK

    @mock.patch("healthcheck.views.HelpDeskCreds")
    def test_database_down_returns_service_unavailable(self, mock_help_desk_creds):
        mock_help_desk_creds.objects.all.side_effect = raise_exception
        view = HealthCheckView()

        status = view.get_status_code()

        assert status == HTTPStatus.SERVICE_UNAVAILABLE


class TestHealthCheckResponses:
    @mock.patch("healthcheck.views.HelpDeskCreds")
    def test_response_ok_in_response(self, mock_help_desk_creds, client):
        response = client.get(reverse("healthcheck"))

        assert response.status_code == HTTPStatus.OK

    @mock.patch("healthcheck.views.HelpDeskCreds")
    def test_response_service_unavailable_in_response(self, mock_help_desk_creds, client):
        mock_help_desk_creds.objects.all.side_effect = raise_exception
        response = client.get(reverse("healthcheck"))

        assert response.status_code == HTTPStatus.SERVICE_UNAVAILABLE

    @mock.patch("healthcheck.views.HelpDeskCreds")
    def test_response_ok_code_in_body(self, mock_help_desk_creds, client):
        response = client.get(reverse("healthcheck"))
        response_body = response.content
        root_element = ET.fromstring(response_body)

        status_element = root_element.find(f"status[.='{HTTPStatus.OK.value}']")

        assert status_element is not None

    @mock.patch("healthcheck.views.HelpDeskCreds")
    def test_response_service_unavailable_code_in_body(self, mock_help_desk_creds, client):
        mock_help_desk_creds.objects.all.side_effect = raise_exception
        response = client.get(reverse("healthcheck"))
        response_body = response.content
        root_element = ET.fromstring(response_body)

        status_element = root_element.find(f"status[.='{HTTPStatus.SERVICE_UNAVAILABLE.value}']")

        assert status_element is not None

    @mock.patch("healthcheck.views.HelpDeskCreds")
    def test_response_time_in_response(self, mock_help_desk_creds, client):
        response = client.get(reverse("healthcheck"))
        response_body = response.content
        root_element = ET.fromstring(response_body)

        response_time_element = root_element.find("response_time[.!='']")

        assert response_time_element is not None
        assert re.match(r"\d+\.\d{3}", response_time_element.text) is not None

    @mock.patch("healthcheck.views.HelpDeskCreds")
    def test_response_cache_control_header(self, mock_help_desk_creds, client):
        response = client.get(reverse("healthcheck"))

        assert "Cache-Control" in response.headers  # /PS-IGNORE
        assert (
            response.headers["Cache-Control"] == "no-cache, no-store, must-revalidate"  # /PS-IGNORE
        )
