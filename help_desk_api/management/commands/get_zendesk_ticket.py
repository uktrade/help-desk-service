import base64
import json
import pathlib
from datetime import datetime

import requests
from django.conf import settings
from django.core.management import BaseCommand
from django.urls import reverse

from help_desk_api.models import HelpDeskCreds


class Command(BaseCommand):
    help = "Get a ticket from Zendesk"  # /PS-IGNORE

    groups_path = settings.BASE_DIR / "scripts/zendesk/zendesk_json/groups.json"
    services_path = settings.BASE_DIR / "scripts/zendesk/zendesk_json/services_field_options.json"

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
        parser.add_argument("-i", "--ticketid", type=int, help="Zendesk ticket ID", required=True)
        parser.add_argument(
            "-u",
            "--microservice",
            type=bool,
            help="Use microservice? (False=use Zendesk directly)",
            default=False,
        )
        parser.add_argument(
            "-l",
            "--localhost",
            type=bool,
            help="Use microservice on localhost?",
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

        url_path = reverse("api:ticket", kwargs={"id": options["ticketid"]})
        if options["microservice"]:
            if options["localhost"]:
                url = f"http://localhost:8000{url_path}"
            else:
                url = f"https://help-desk-service-staging.london.cloudapps.digital{url_path}"
        else:
            url = f"https://staging-uktrade.zendesk.com{url_path}"
        # url = f"https://{credentials.zendesk_subdomain}.zendesk.com{url_path}"

        print(f"Getting ticket from {url}")

        response = requests.get(
            url,
            # headers={"Content-Type": "application/json"},
            headers={"Authorization": encoded_auth_header, "Content-Type": "application/json"},
        )

        print(f"Response status: {response.status_code}")

        ticket = response.json()

        if options["output"]:
            output_path = options["output"].with_name(
                options["output"].name.format(
                    ticketid=options["ticketid"], timestamp=datetime.utcnow().isoformat()
                )
            )
            output_path = settings.BASE_DIR / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as output_file:
                json.dump(ticket, output_file, indent=4)
                print(f"Output written to {output_path}")
        else:
            json.dump(ticket, self.stdout, indent=4)
