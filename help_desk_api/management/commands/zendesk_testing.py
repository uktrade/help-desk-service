import base64
import json
import pathlib
from datetime import datetime

import requests
from django.conf import settings
from django.core.management import BaseCommand

from help_desk_api.models import HelpDeskCreds


class Command(BaseCommand):
    help = "Create ticket on Zendesk"  # /PS-IGNORE

    def __init__(self, stdout=None, stderr=None, **kwargs):
        super().__init__(stdout, stderr, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            "-c",
            "--credentials",
            type=str,
            help="Email address linked to Halo credentials",
            required=True,
        )
        parser.add_argument(
            "-t",
            "--token",
            type=str,
            help="Zendesk API token",
            required=True,
        )
        parser.add_argument(
            "-u",
            "--microservice",
            type=bool,
            help="Zendesk API token",
            default=False,
        )
        parser.add_argument(
            "-o", "--output", type=pathlib.Path, help="Output file path (default: stdout)"
        )

    def handle(self, *args, **options):
        credentials = HelpDeskCreds.objects.get(zendesk_email=options["credentials"])

        auth_header = f"{credentials.zendesk_email}/token:{options['token']}"
        encoded_auth_header = (
            f"Basic {base64.b64encode(bytes(auth_header, 'utf-8')).decode('ascii')}"  # /PS-IGNORE
        )

        ticket_id = 34865

        if options["microservice"]:
            url = "https://<ADD MICROSERVICE DOMAIN HERE>" "/api/v2/tickets/34865.json"
        else:
            url = "https://<ADD ZENDESK DOMAIN HERE>/api/v2/tickets/34865.json"

        response = requests.get(
            url,
            headers={
                "Authorization": encoded_auth_header,
                "Content-Type": "application/json",
            },
        )

        timestamp = datetime.utcnow().isoformat()
        if options["output"]:
            output_path = options["output"].with_name(
                options["output"].name.format(ticketid=ticket_id, timestamp=timestamp)
            )
            output_path = settings.BASE_DIR / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as output_file:
                json.dump(response.json(), output_file, indent=4)
                print(f"Output written to {output_path}")
        else:
            json.dump(response.json(), self.stdout, indent=4)
