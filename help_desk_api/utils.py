import base64

from rest_framework import authentication, exceptions


def get_zenpy_request_vars(request):
    encoded_auth = authentication.get_authorization_header(request)
    if not encoded_auth:
        raise exceptions.NotAuthenticated("No Authorization header found")
    auth_parts = encoded_auth.decode("utf-8").split(" ")

    auth_header = base64.b64decode(auth_parts[1])  # /PS-IGNORE
    creds_parts = auth_header.decode("utf-8").split(":")

    email = creds_parts[0].replace("/token", "")

    try:
        token = creds_parts[1]
    except UnicodeError:
        msg = "Invalid token header. Token string should not contain invalid characters."
        raise exceptions.AuthenticationFailed(msg)

    return token, email
