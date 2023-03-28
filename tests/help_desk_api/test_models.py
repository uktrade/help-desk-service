from unittest import mock

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ValidationError
from django.test import Client
from django.urls import reverse

from help_desk_api.models import HelpDeskCreds

pytestmark = pytest.mark.django_db


class TestZendeskRequiredSetting:
    def test_zendesk_required_fails_when_only_halo_creds_supplied(self, zendesk_required_settings):
        with pytest.raises(ValidationError):
            HelpDeskCreds.objects.create(
                zendesk_email="test@example.com",  # /PS-IGNORE
                zendesk_token="ABC123",
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
    """
    Some of these tests exist because an earlier implementation of `HelpDeskCreds`
    attempted to encrypt `zendesk_token`. This responsibility is now on clients of the class
    which should call `set_token` on the newly-created instance.
    At an application level, token encryption is performed by the admin forms.
    """

    @mock.patch("help_desk_api.models.HelpDeskCreds.set_token")
    def test_set_token_not_called_on_queryset_create(
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
        set_token.assert_not_called()

    def test_zendesk_token_not_encrypted_on_model_save(self, zendesk_required_settings):
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
        assert expected_token == db_help_desk_creds.zendesk_token

    @mock.patch("help_desk_api.models.HelpDeskCreds.set_token")
    def test_help_desk_creds_admin_calls_set_token(self, set_token: mock.MagicMock, client: Client):
        user_model = get_user_model()
        user_password = "dumb_password"
        user = user_model.objects.create_superuser(
            username="superuser", password=user_password, email="test@example.com"  # /PS-IGNORE
        )
        client.login(username=user.username, password=user_password)
        data = {
            "zendesk_token": "test_zendesk_token",
            "zendesk_email": "test@example.com",  # /PS-IGNORE
            "help_desk": HelpDeskCreds.HelpDeskChoices.ZENDESK.value,
            "_save": "Save",
        }
        url = reverse(f"admin:{HelpDeskCreds._meta.app_label}_{HelpDeskCreds._meta.model_name}_add")
        client.post(url, data=data)
        set_token.assert_called_once_with(data["zendesk_token"])

    def test_help_desk_creds_admin_encrypts_zendesk_token(self, client: Client):
        user_model = get_user_model()
        user_password = "dumb_password"
        user = user_model.objects.create_superuser(
            username="superuser", password=user_password, email="test@example.com"  # /PS-IGNORE
        )
        client.login(username=user.username, password=user_password)
        zendesk_email = "test@example.com"  # /PS-IGNORE
        zendesk_token = "test_zendesk_token"
        data = {
            "zendesk_token": zendesk_token,
            "zendesk_email": zendesk_email,
            "help_desk": HelpDeskCreds.HelpDeskChoices.ZENDESK.value,
            "_save": "Save",
        }
        url = reverse(f"admin:{HelpDeskCreds._meta.app_label}_{HelpDeskCreds._meta.model_name}_add")
        client.post(url, data=data)
        credentials = HelpDeskCreds.objects.get(zendesk_email=zendesk_email)
        assert check_password(zendesk_token, credentials.zendesk_token)
