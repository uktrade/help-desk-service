import base64
import json
import pathlib
from datetime import datetime

import requests
from django.conf import settings
from django.core.management import BaseCommand

from help_desk_api.models import HelpDeskCreds


class Command(BaseCommand):
    help = "Get all Group records from the Zendesk API"  # /PS-IGNORE

    def __init__(self, stdout=None, stderr=None, **kwargs):
        super().__init__(stdout, stderr, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            "-c",
            "--credentials",
            type=str,
            help="Email address linked to Zendesk credentials",
            required=True,
        )
        parser.add_argument(
            "-t",
            "--token",
            type=str,
            help="Zendesk API token",  # /PS-IGNORE
            required=True,
        )
        parser.add_argument("-f", "--fieldid", type=int, required=True, help="Field ID")
        parser.add_argument(
            "-o", "--output", type=pathlib.Path, help="Output file path (default: stdout)"
        )

    def handle(self, *args, **options):
        credentials = HelpDeskCreds.objects.get(zendesk_email=options["credentials"])
        auth_header = f"{credentials.zendesk_email}/token:{options['token']}"
        encoded_auth_header = (
            f"Basic {base64.b64encode(bytes(auth_header, 'utf-8')).decode('ascii')}"  # /PS-IGNORE
        )

        field_id = options["fieldid"]
        url_path = f"/api/v2/ticket_fields/{field_id}"
        url = f"https://{credentials.zendesk_subdomain}.zendesk.com{url_path}"

        print(f"Getting field from {url}")

        response = requests.get(
            url,
            headers={"Authorization": encoded_auth_header, "Content-Type": "application/json"},
        )

        field_response = response.json()

        output = field_response["ticket_field"]

        if options["output"]:
            output_path = options["output"].with_name(
                options["output"].name.format(
                    subdomain=credentials.zendesk_subdomain,
                    field_id=field_id,
                    field_name=output["raw_title"],
                    timestamp=datetime.utcnow().isoformat(),
                )
            )
            output_path = settings.BASE_DIR / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as output_file:
                json.dump(output, output_file, indent=4)
        else:
            json.dump(output, self.stdout, indent=4)

    def get_zendesk_data(self, credentials):
        credentials = HelpDeskCreds.objects.get(zendesk_email=credentials)
        # TODO: handle authorisation for Zendesk
        api_url = f"https://{credentials.zendesk_subdomain}.zendesk.com/api/v2/groups"
        response = requests.get(api_url)
        return response.json()
