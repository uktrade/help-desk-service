from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from help_desk_api.models import HelpDeskCreds


class HelpDeskCredsChangeForm(forms.ModelForm):
    zendesk_token = ReadOnlyPasswordHashField(
        label="Zendesk token",
        help_text="Raw tokens are not stored, so there is no way to see this "
        "token, but you can change the token using "
        '<a href="{}">this form</a>.',
    )

    class Meta:
        model = HelpDeskCreds
        fields = (
            "zendesk_email",
            "zendesk_token",
            "zendesk_subdomain",
            "halo_client_id",
            "halo_client_secret",
            "help_desk",
            "note",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        zendesk_token = self.fields.get("zendesk_token")
        if zendesk_token:
            zendesk_token.help_text = zendesk_token.help_text.format("../zendesk_token/")


class HelpDeskCredsCreationForm(forms.ModelForm):
    class Meta:
        model = HelpDeskCreds
        fields = (
            "zendesk_email",
            "zendesk_token",
            "zendesk_subdomain",
            "halo_client_id",
            "halo_client_secret",
            "help_desk",
            "note",
        )

    def save(self, commit=True):
        credentials: HelpDeskCreds = super().save(commit=False)
        credentials.set_token(self.cleaned_data["zendesk_token"])
        if commit:
            credentials.save()
        return credentials
