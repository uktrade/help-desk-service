from typing import TYPE_CHECKING, Optional

from authbroker_client.backends import AuthbrokerBackend
from authbroker_client.utils import get_client, get_profile, has_valid_token
from django.contrib.auth import get_user_model

if TYPE_CHECKING:
    from user.models import User
else:
    User = get_user_model()


class CustomAuthbrokerBackend(AuthbrokerBackend):
    def authenticate(self, request, **kwargs):
        client = get_client(request)
        if has_valid_token(client):
            profile = get_profile(client)
            return self.get_or_create_user(profile)
        return None

    @staticmethod
    def get_or_create_user(profile):
        user: Optional[User] = User.objects.filter(username=profile["email_user_id"]).first()

        if user:
            user.username = profile["email_user_id"]
            user.email = profile["email"]  # might change over time
            user.sso_contact_email = profile["contact_email"]  # might change over time
            user.first_name = profile["first_name"]  # might change over time
            user.last_name = profile["last_name"]  # might change over time
            user.sso_legacy_user_id = profile["user_id"]
            user.sso_email_user_id = profile["email_user_id"]
        else:
            user = User(
                username=profile["email_user_id"],
                email=profile["email"],
                sso_contact_email=profile["contact_email"],
                first_name=profile["first_name"],
                last_name=profile["last_name"],
                sso_legacy_user_id=profile["user_id"],
                sso_email_user_id=profile["email_user_id"],
            )

        user.set_unusable_password()
        user.save()

        return user
