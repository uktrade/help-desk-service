from unittest import mock

import pytest
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError

from help_desk_api.models import HelpDeskCreds

pytestmark = pytest.mark.django_db


class TestZendeskRequiredSetting:
    def test_zendesk_required_fails_when_only_halo_creds_supplied(self, zendesk_required_settings):
        with pytest.raises(ValidationError):
            HelpDeskCreds.objects.create(
                zendesk_email="test@example.com",  # /PS-IGNORE
                halo_client_id="test_halo_client_id",
                halo_client_secret="test_halo_client_secret",
                help_desk=[
                    HelpDeskCreds.HelpDeskChoices.HALO,
                ],
            )

    def test_zendesk_required_succeeds_when_zendesk_token_supplied(self, zendesk_required_settings):
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


class TestZendeskTokenEncryption:
    @mock.patch("help_desk_api.models.HelpDeskCreds.set_token")
    def test_set_token_called_on_queryset_create(
        self, set_token: mock.MagicMock, zendesk_required_settings
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

    def test_zendesk_token_encrypted_on_queryset_create(self, zendesk_required_settings):
        expected_token = "test_zendesk_token"
        help_desk_creds = HelpDeskCreds.objects.create(
            zendesk_email="test@example.com",  # /PS-IGNORE
            zendesk_token=expected_token,
            help_desk=[
                HelpDeskCreds.HelpDeskChoices.ZENDESK,
            ],
        )
        assert check_password(expected_token, help_desk_creds.zendesk_token)

    def test_set_token_not_called_on_queryset_get(self, zendesk_required_settings):
        expected_token = "test_zendesk_token"
        help_desk_creds = HelpDeskCreds.objects.create(
            zendesk_email="test@example.com",  # /PS-IGNORE
            zendesk_token=expected_token,
            help_desk=[
                HelpDeskCreds.HelpDeskChoices.ZENDESK,
            ],
        )
        pk = help_desk_creds.pk
        with mock.patch("help_desk_api.models.HelpDeskCreds.set_token") as set_token:
            HelpDeskCreds.objects.get(pk=pk)
            set_token.assert_not_called()

    def test_zendesk_token_correct_on_queryset_get(self, zendesk_required_settings):
        expected_token = "test_zendesk_token"
        help_desk_creds = HelpDeskCreds.objects.create(
            zendesk_email="test@example.com",  # /PS-IGNORE
            zendesk_token=expected_token,
            help_desk=[
                HelpDeskCreds.HelpDeskChoices.ZENDESK,
            ],
        )
        pk = help_desk_creds.pk

        db_help_desk_creds = HelpDeskCreds.objects.get(pk=pk)

        assert check_password(expected_token, db_help_desk_creds.zendesk_token)

    def test_zendesk_token_matches_initial_token_on_queryset_get(self, zendesk_required_settings):
        expected_token = "test_zendesk_token"
        help_desk_creds = HelpDeskCreds.objects.create(
            zendesk_email="test@example.com",  # /PS-IGNORE
            zendesk_token=expected_token,
            help_desk=[
                HelpDeskCreds.HelpDeskChoices.ZENDESK,
            ],
        )
        pk = help_desk_creds.pk
        db_help_desk_creds = HelpDeskCreds.objects.get(pk=pk)
        assert check_password(expected_token, db_help_desk_creds.zendesk_token)

    def test_zendesk_token_encrypted_on_model_save(self, zendesk_required_settings):
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

    def test_zendesk_token_encrypted_on_constructed_instance_save(self, zendesk_required_settings):
        initial_token = "test_zendesk_token"
        help_desk_creds = HelpDeskCreds(
            zendesk_email="test@example.com",  # /PS-IGNORE
            zendesk_token=initial_token,
            help_desk=[
                HelpDeskCreds.HelpDeskChoices.ZENDESK,
            ],
        )
        with mock.patch("help_desk_api.models.HelpDeskCreds.set_token") as set_token:
            help_desk_creds.save()

        set_token.assert_called_once_with(initial_token)
