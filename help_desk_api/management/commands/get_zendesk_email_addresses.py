import base64
import json
import pathlib
from datetime import datetime

import requests
from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "Get all Email addresses from the Zendesk API"  # /PS-IGNORE

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
        parser.add_argument("-p", "--prefix", type=str, help="Zendesk instance", default="uktrade")
        parser.add_argument(
            "-o", "--output", type=pathlib.Path, help="Output file path (default: stdout)"
        )

    def handle(self, *args, **options):
        prefix = options.get("prefix")
        zendesk_email = options.get("credentials")
        zendesk_token = options.get("token")
        # This means we try a real request to Zendesk
        emails = self.get_zendesk_data(prefix, zendesk_email, zendesk_token)

        if options["output"]:
            output_path = options["output"].with_name(
                options["output"].name.format(
                    prefix=prefix, timestamp=datetime.utcnow().isoformat()
                )
            )
            output_path = settings.BASE_DIR / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as output_file:
                print(f"Writing response to {output_path}")
                json.dump(emails, output_file, indent=4)
        else:
            json.dump(emails, self.stdout, indent=4)

        email_addresses = [f"{datum['email']}\n" for datum in emails["recipient_addresses"]]
        if options["output"]:
            output_path: pathlib.Path = options["output"].with_name(
                options["output"].name.format(
                    prefix=prefix, timestamp=datetime.utcnow().isoformat()
                )
            )
            output_path = output_path.with_suffix(".txt")
            output_path = settings.BASE_DIR / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as output_file:
                print(f"Writing response to {output_path}")
                # json.dump(email_addresses, output_file, indent=4)
                output_file.writelines(email_addresses)
        else:
            json.dump(email_addresses, self.stdout, indent=4)

    def get_zendesk_data(self, prefix, zendesk_email, zendesk_token):
        auth_header = f"{zendesk_email}/token:{zendesk_token}"
        encoded_auth_header = (
            f"Basic {base64.b64encode(bytes(auth_header, 'utf-8')).decode('ascii')}"  # /PS-IGNORE
        )
        api_url = f"https://{prefix}.zendesk.com/api/v2/recipient_addresses"
        response = requests.get(
            api_url,
            headers={"Authorization": encoded_auth_header, "Content-Type": "application/json"},
        )
        return response.json()
