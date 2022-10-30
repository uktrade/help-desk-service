import base64

from rest_framework import authentication, exceptions


def get_request_token(request):
    encoded_auth = authentication.get_authorization_header(request)
    auth_parts = encoded_auth.decode("utf-8").split(" ")
    auth_header = base64.b64decode(auth_parts[1])  # /PS-IGNORE

    token = auth_header.decode("utf-8").split(":")[1]

    try:
        token = auth_header.decode("utf-8").split(":")[1]
    except UnicodeError:
        msg = "Invalid token header. Token string should not contain invalid characters."
        raise exceptions.AuthenticationFailed(msg)

    return token
