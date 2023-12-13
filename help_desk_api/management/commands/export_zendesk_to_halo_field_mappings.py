import base64
import json
import pathlib
from csv import DictWriter
from datetime import datetime

import requests
from django.conf import settings
from django.core.management import BaseCommand

from help_desk_api.models import HelpDeskCreds


class Command(BaseCommand):
    help = "Associate Zendesk custom fields with Halo equivalents"  # /PS-IGNORE

    def __init__(self, stdout=None, stderr=None, **kwargs):
        super().__init__(stdout, stderr, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            "-c",
            "--credentials",
            type=str,
            help="Email address for Zendesk credentials in DB",
            required=True,
        )
        parser.add_argument(
            "-t",
            "--token",
            type=str,
            help="Zendesk API token",  # /PS-IGNORE
            required=True,
        )
        parser.add_argument("-p", "--prefix", type=str, help="Zendesk instance", default="uktrade")
        parser.add_argument(
            "-o", "--output", type=pathlib.Path, help="Output file path (default: stdout)"
        )

    def handle(self, *args, **options):
        credentials = HelpDeskCreds.objects.get(zendesk_email=options["credentials"])
        zendesk_token = options["token"]

        auth_header = f"{credentials.zendesk_email}/token:{zendesk_token}"
        encoded_auth_header = (
            f"Basic {base64.b64encode(bytes(auth_header, 'utf-8')).decode('ascii')}"  # /PS-IGNORE
        )

        url_path = "/api/v2/ticket_fields"
        url = f"https://{credentials.zendesk_subdomain}.zendesk.com{url_path}"

        print(f"Getting ticket fields from {url}")

        response = requests.get(
            url,
            headers={"Authorization": encoded_auth_header, "Content-Type": "application/json"},
        )

        zendesk_response = response.json()
        zendesk_ticket_fields = zendesk_response["ticket_fields"]

        zendesk_ticket_data = [
            {"zendesk_id": ticket_field["id"], "zendesk_title": ticket_field["raw_title"]}
            for ticket_field in zendesk_ticket_fields
        ]

        output = zendesk_ticket_data

        if options["output"]:
            output_path = options["output"].with_name(
                options["output"].name.format(
                    timestamp=datetime.utcnow().isoformat(), prefix=options["prefix"]
                )
            )
            output_path = settings.BASE_DIR / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8-sig") as output_file:
                writer = DictWriter(
                    output_file,
                    [
                        "zendesk_id",
                        "zendesk_title",
                        "is_zendesk_custom_field",
                        "halo_id",
                        "halo_title",
                        "special_treatment",
                    ],
                    extrasaction="ignore",
                    dialect="excel",
                )
                writer.writeheader()
                writer.writerows(output)
        else:
            writer = DictWriter(
                self.stdout,
                [
                    "zendesk_id",
                    "zendesk_title",
                    "is_zendesk_custom_field",
                    "halo_id",
                    "halo_title",
                    "special_treatment",
                ],
                extrasaction="ignore",
                dialect="excel",
            )
            writer.writeheader()
            writer.writerows(output)

    def load_groups(self, groups_file_path):
        with open(groups_file_path, "r") as groups_file:
            groups_data = json.load(groups_file)
        groups = {
            str(group["id"]): group["name"]
            for group in groups_data["groups"]
            if group["deleted"] is False
        }
        return groups

    def load_fields(self, fields_file_path):
        with open(fields_file_path, "r") as fields_file:
            fields_data = json.load(fields_file)
        fields = {
            str(field["id"]): field["raw_title"] if field["raw_title"] else field["title"]
            for field in fields_data["ticket_fields"]
        }
        return fields
