from http import HTTPStatus
from unittest import mock
from unittest.mock import MagicMock

from django.conf import settings
from django.core.cache import caches
from django.http import HttpResponse
from django.urls import reverse


@mock.patch("halo.halo_manager.HaloAPIClient._HaloAPIClient__authenticate", return_value="abc123")
@mock.patch("halo.halo_api_client.requests.get")
@mock.patch("halo.halo_api_client.requests.post")
class TestGreatForms:
    def test_great_international_contact_form(
        self,
        _mock_post: MagicMock,
        _mock_get: MagicMock,
        _mock_authenticate: MagicMock,
        zendesk_authorization_header,
        halo_creds_only,
        great_international_contact_form_bad_service,
        client,
    ):
        """
        Great was sending a duff value for Service, so check it causes a 500
        """
        user_id = great_international_contact_form_bad_service["ticket"]["requester_id"]
        user_cache = caches[settings.USER_DATA_CACHE]
        user_cache.set(
            user_id, {"user": {"name": "Test name", "email": "test@example.com"}}  # /PS-IGNORE
        )  # /PS-IGNORE
        url = reverse("api:tickets")

        response: HttpResponse = client.post(
            url,
            data=great_international_contact_form_bad_service,
            headers={"Authorization": zendesk_authorization_header},
            content_type="application/json",
        )

        assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
