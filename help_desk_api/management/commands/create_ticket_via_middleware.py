import base64
import json
import pathlib
from datetime import datetime

import requests
from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "Create ticket on Zendesk via middleware"  # /PS-IGNORE

    environments = {
        "local": "http://localhost:8000/",
        "staging": "https://help-desk-service-staging.london.cloudapps.digital/",
        "prod": "https://help-desk-service.london.cloudapps.digital/",
    }

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
            "-e",
            "--environment",
            type=str,
            help="Environment (default: localhost)",
            default="local",
        )
        parser.add_argument(
            "-o", "--output", type=pathlib.Path, help="Output file path (default: stdout)"
        )

    def handle(self, *args, **options):
        auth_header = f"{options['credentials']}/token:{options['token']}"
        encoded_auth_header = (
            f"Basic {base64.b64encode(bytes(auth_header, 'utf-8')).decode('ascii')}"  # /PS-IGNORE
        )
        host = self.environments[options["environment"]]
        url = f"{host}api/v2/tickets.json"

        timestamp = datetime.utcnow().isoformat()
        via = f"via {options['environment']}"
        subject = f"Posted {via} at {timestamp}"
        description = """
        Some description.

        It has several lines.

        Like this.

        This one is posted as a comment rather than a description, as Zendesk say it should be.
        """

        response = requests.post(
            url,
            headers={"Authorization": encoded_auth_header, "Content-Type": "application/json"},
            data=json.dumps(
                {
                    "ticket": {
                        "subject": subject,
                        "comment": {
                            "body": description,
                        },
                    }
                }
            ),
        )

        print(response.status_code)

        ticket = response.json()["ticket"]
        ticket_id = ticket["id"] if "id" in ticket else "xyzzzy"

        if options["output"]:
            output_path = options["output"].with_name(
                options["output"].name.format(ticketid=ticket_id, timestamp=timestamp)
            )
            output_path = settings.BASE_DIR / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as output_file:
                json.dump(ticket, output_file, indent=4)
                print(f"Output written to {output_path}")
        else:
            json.dump(ticket, self.stdout, indent=4)
