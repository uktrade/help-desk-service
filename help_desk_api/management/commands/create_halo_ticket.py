import json
import pathlib
from datetime import datetime

from django.conf import settings
from django.core.management import BaseCommand
from halo.halo_api_client import HaloAPIClient

from help_desk_api.models import HelpDeskCreds


class Command(BaseCommand):
    help = "Create ticket on Halo"  # /PS-IGNORE

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
            "-o", "--output", type=pathlib.Path, help="Output file path (default: stdout)"
        )

    def handle(self, *args, **options):
        credentials = HelpDeskCreds.objects.get(zendesk_email=options["credentials"])
        halo_client = HaloAPIClient(
            client_id=credentials.halo_client_id, client_secret=credentials.halo_client_secret
        )

        ticket_data = [
            {
                "site_id": 18,
                "summary": f"""Halo via API at {datetime.utcnow().isoformat()}""",  # /PS-IGNORE
                "details": "Blah",
                "tags": [{"text": "bug"}],
                "customfields": [
                    {"name": "CFBrowser", "value": "Safari 16.3, Macos 10.15.7"},  # /PS-IGNORE
                    {"name": "CFService", "value": "datahub"},
                    {
                        "name": "CFESSBusinessType",
                        "value": [
                            {
                                "id": "38",
                            }
                        ],
                    },
                ],
                "users_name": "Some Body",
                "reportedby": "somebody@example.com",  # /PS-IGNORE
                "dont_do_rules": False,
            }
        ]

        response = halo_client.post(
            "Tickets", payload=ticket_data
        )  # expects an array even for one ticket

        if options["output"]:
            output_path = options["output"].with_name(
                options["output"].name.format(
                    ticketid=response["id"], timestamp=datetime.utcnow().isoformat()
                )
            )
            output_path = settings.BASE_DIR / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as output_file:
                json.dump(response, output_file, indent=4)
                print(f"Output written to {output_path}")
        else:
            json.dump(response, self.stdout, indent=4)
