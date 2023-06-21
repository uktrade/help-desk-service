import base64

from halo.halo_api_client import HaloAPIClient
from rest_framework import authentication, exceptions

from help_desk_api.models import HelpDeskCreds


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


def make_halo_teams_from_zendesk_groups(halo_credentials, zendesk_groups):
    credentials = HelpDeskCreds.objects.get(zendesk_email=halo_credentials)
    halo_client = HaloAPIClient(
        client_id=credentials.halo_client_id, client_secret=credentials.halo_client_secret
    )
    existing_halo_teams = halo_client.get("/Team")
    halo_teams_by_name = {
        existing_halo_team["name"]: existing_halo_team for existing_halo_team in existing_halo_teams
    }
    for group in zendesk_groups["groups"]:
        if group["name"] in halo_teams_by_name:
            print(f"Existing Halo team for group {group['name']}")
        else:
            print(f"Group {group['name']} isn't a Team yet yet - creating now…")  # /PS-IGNORE
            halo_client.post("/Team", payload=[{"name": group["name"]}])
            break  # TODO: remove; this is just here to limit to one group for experimentation
