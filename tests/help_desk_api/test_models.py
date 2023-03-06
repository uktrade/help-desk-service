from unittest import mock

import pytest
from django.core.exceptions import ValidationError

from help_desk_api.models import HelpDeskCreds


@pytest.fixture()
def zendesk_required_settings(settings):
    settings.REQUIRE_ZENDESK = True


@pytest.fixture()
def zendesk_not_required_settings(settings):
    settings.REQUIRE_ZENDESK = False


pytestmark = pytest.mark.django_db


def test_zendesk_required_setting_fails_for_halo_only(zendesk_required_settings):
    with pytest.raises(ValidationError):
        HelpDeskCreds.objects.create(
            zendesk_email="test@example.com",  # /PS-IGNORE
            halo_client_id="test_halo_client_id",
            halo_client_secret="test_halo_client_secret",
            help_desk=[
                HelpDeskCreds.HelpDeskChoices.HALO,
            ],
        )


def test_zendesk_required_setting_succeeds_with_zendesk_token(zendesk_required_settings):
    try:
        HelpDeskCreds.objects.create(
            zendesk_email="test@example.com",  # /PS-IGNORE
            halo_client_id="test_halo_client_id",
            halo_client_secret="test_halo_client_secret",
            zendesk_token="test_zendesk_token",
            help_desk=[
                HelpDeskCreds.HelpDeskChoices.ZENDESK,
                HelpDeskCreds.HelpDeskChoices.HALO,
            ],
        )
    except ValidationError as e:
        assert False, f"ValidationError raised incorrectly. Messages: {e.messages}"


@mock.patch("help_desk_api.models.HelpDeskCreds.set_token")
def test_zendesk_token_encrypted_on_queryset_create(
    set_token: mock.MagicMock, zendesk_required_settings
):
    expected_token = "test_zendesk_token"
    HelpDeskCreds.objects.create(
        zendesk_email="test@example.com",  # /PS-IGNORE
        zendesk_token=expected_token,
        help_desk=[
            HelpDeskCreds.HelpDeskChoices.ZENDESK,
        ],
    )
    set_token.assert_called_once_with(expected_token)


def test_zendesk_token_encrypted_on_model_save(zendesk_required_settings):
    initial_token = "test_zendesk_token"
    help_desk_creds = HelpDeskCreds.objects.create(
        zendesk_email="test@example.com",  # /PS-IGNORE
        zendesk_token=initial_token,
        help_desk=[
            HelpDeskCreds.HelpDeskChoices.ZENDESK,
        ],
    )
    new_token = "test_zendesk_token_changed"

    help_desk_creds.zendesk_token = new_token
    with mock.patch("help_desk_api.models.HelpDeskCreds.set_token") as set_token:
        help_desk_creds.save()

    set_token.assert_called_once_with(new_token)
