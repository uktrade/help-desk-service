from django.contrib.auth.hashers import check_password
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

from help_desk_api.models import HelpDeskCreds
from help_desk_api.utils import get_zenpy_request_vars


class ZenpyAuthentication(authentication.TokenAuthentication):
    def authenticate(self, request):
        try:
            token, email = get_zenpy_request_vars(request)
        except:  # noqa E722
            AuthenticationFailed("Could not parse auth request header value")

        creds = HelpDeskCreds.filter(email=email).first()

        if not creds:
            raise AuthenticationFailed("User associated with this email not found")

        if check_password(token, creds.zendesk_token):
            return (creds, None)
        else:
            raise AuthenticationFailed("Invalid credentials")
