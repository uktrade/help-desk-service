import json
import pathlib
from datetime import datetime

from django.conf import settings
from django.core.management import BaseCommand
from halo.halo_api_client import HaloAPIClient

from help_desk_api.models import HelpDeskCreds

# from help_desk_api.utils.field_mappings import ZendeskToHaloMappings


class Command(BaseCommand):
    help = "Get Halo Ticket Rules"  # /PS-IGNORE

    def __init__(self, stdout=None, stderr=None, **kwargs):
        super().__init__(stdout, stderr, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            "-c",
            "--credentials",
            type=str,
            help="Email address linked to Zendesk and Halo credentials",
            required=True,
        )
        # parser.add_argument(
        #     "-t",
        #     "--token",
        #     type=str,
        #     help="Zendesk API token",
        #     required=True,
        # )
        # parser.add_argument(
        #     "-f", "--fields", type=pathlib.Path, help="Zendesk fields JSON file path"
        # )
        # parser.add_argument(
        #     "-p", "--prefix", type=str, help="Zendesk instance", default="uktrade"
        # )
        parser.add_argument(
            "-o", "--output", type=pathlib.Path, help="Output file path (default: stdout)"
        )

    def handle(self, *args, **options):
        credentials = HelpDeskCreds.objects.get(zendesk_email=options["credentials"])

        halo_client = HaloAPIClient(
            client_id=credentials.halo_client_id, client_secret=credentials.halo_client_secret
        )

        halo_fields_data = halo_client.get("TicketRules")

        output = halo_fields_data

        if options["output"]:
            output_path = options["output"].with_name(
                options["output"].name.format(
                    timestamp=datetime.utcnow().isoformat(),
                )
            )
            output_path = settings.BASE_DIR / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8-sig") as output_file:
                json.dump(output, output_file, indent=4)
        else:
            json.dump(output, self.stdout, indent=4)
