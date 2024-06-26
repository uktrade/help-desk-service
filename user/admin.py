from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

User = get_user_model()


class SSOUserAdmin(UserAdmin):
    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    # make everything read only for non-super users
    def get_readonly_fields(self, request, obj=None):
        if obj and not request.user.is_superuser:
            self.readonly_fields = [field.name for field in obj.__class__._meta.fields]
        return self.readonly_fields

    # exclude = ("password",)
    fieldsets = (
        ("Personal info", {"fields": ("first_name", "last_name", "email", "password")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
    )


admin.site.register(User, SSOUserAdmin)
