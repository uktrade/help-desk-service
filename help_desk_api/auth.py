from rest_framework import authentication

from help_desk_api.utils import get_request_token


class ZenpyAuthentication(authentication.TokenAuthentication):
    def authenticate(self, request):
        token = get_request_token(request)

        return self.authenticate_credentials(token)
