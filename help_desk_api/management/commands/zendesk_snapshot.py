import base64
import json
import pathlib

import requests
from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "Create snapshot of Zendesk configuration"  # /PS-IGNORE

    snapshot_endpoints = [
        "ticket_forms",
        "ticket_fields",
        "custom_statuses",
        "sharing_agreements",
        "user_fields",
        "organizations",
        "organization_fields",
        "tags",
        "business_hours/schedules",
        "views",
        "triggers",
        "trigger_categories",
        "macros",
        "automations",
        "slas/policies",
        "custom_roles",
        "brands",
    ]

    def __init__(self, stdout=None, stderr=None, **kwargs):
        super().__init__(stdout, stderr, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            "-e",
            "--email",
            type=str,
            help="Email address linked to Zendesk credentials",
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
            "-z",
            "--zendesk_url",
            type=str,
            help="Zendesk URL",
            required=True,
        )
        parser.add_argument(
            "-p",
            "--prefix",
            type=str,
            help="Zendesk prefix",
            default="uktrade",
            required=True,
        )
        parser.add_argument(
            "-o", "--output", type=pathlib.Path, help="Output path (default: stdout)"
        )

    def handle(self, *args, **options):
        output_path = options["output"]
        absolute_output_path = settings.BASE_DIR / output_path / options["prefix"]

        auth_header = f"{options['email']}/token:{options['token']}"
        encoded_auth_header = (
            f"Basic {base64.b64encode(bytes(auth_header, 'utf-8')).decode('ascii')}"  # /PS-IGNORE
        )

        zendesk_url = options["zendesk_url"]
        url_template = "{zendesk_url}/api/v2/{endpoint}.json"

        for endpoint in self.snapshot_endpoints:
            url = url_template.format(zendesk_url=zendesk_url, endpoint=endpoint)
            print(f"Getting {url}…")
            response = requests.get(
                url,
                headers={"Authorization": encoded_auth_header, "Content-Type": "application/json"},
            )

            file_output_path = absolute_output_path / f"{endpoint.replace('/', '__')}.json"
            print(f"Saving to {file_output_path}")
            file_output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(file_output_path, "w") as output_file:
                json.dump(response.json(), output_file, indent=4)
            print(f"Saved {file_output_path}")
