from django.contrib import admin

from help_desk_api.models import CustomField, HelpDeskCreds, Value

from .forms import HelpDeskCredsChangeForm, HelpDeskCredsCreationForm


@admin.register(HelpDeskCreds)
class HelpDeskCredsAdmin(admin.ModelAdmin):
    form = HelpDeskCredsChangeForm
    add_form = HelpDeskCredsCreationForm
    list_display = [
        "note",
        "zendesk_email",
        "zendesk_subdomain",
        "help_desk",
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


@admin.register(CustomField)
class CustomFieldAdmin(admin.ModelAdmin):
    fieldsets = [
        (
            None,
            {
                "fields": [
                    ("zendesk_name", "halo_name"),
                    ("zendesk_id", "halo_id"),
                ],
            },
        ),
        (
            "Values",
            {
                "fields": ["values"],
            },
        ),
    ]
    ordering = (
        "zendesk_name",
        "zendesk_id",
    )
    list_display = [
        "zendesk_name",
        "zendesk_id",
        "halo_name",
        "halo_id",
        "is_multiselect",
        "is_selection",
    ]
    list_filter = [
        "is_multiselect",
    ]
    search_fields = [
        "zendesk_name",
        "zendesk_id",
        "halo_name",
        "halo_id",
        "values__zendesk_value",
    ]
    filter_horizontal = ("values",)


@admin.register(Value)
class ValueAdmin(admin.ModelAdmin):
    list_display = ["zendesk_field_name_display", "zendesk_value", "halo_id"]
    ordering = [
        "halo_id",
        "field__zendesk_name",
        "zendesk_value",
    ]
    search_fields = [
        "field__zendesk_name",
        "zendesk_value",
    ]
