from django.contrib import admin

from help_desk_api.models import HelpDeskCreds

from .forms import HelpDeskCredsChangeForm, HelpDeskCredsCreationForm


@admin.register(HelpDeskCreds)
class HelpDeskCredsAdmin(admin.ModelAdmin):
    form = HelpDeskCredsChangeForm
    add_form = HelpDeskCredsCreationForm
    list_display = [
        "zendesk_email",
        "zendesk_subdomain",
        "help_desk",
        "note",
    ]

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during credentials creation
        This is lifted from django.contrib.auth.admin.UserAdmin  /PS-IGNORE
        """
        defaults = {}
        if obj is None:
            defaults["form"] = self.add_form
        defaults.update(kwargs)
        return super().get_form(request, obj, **defaults)
