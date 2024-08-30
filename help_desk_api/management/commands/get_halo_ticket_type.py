import json
import pathlib
from datetime import datetime

from django.conf import settings
from django.core.management import BaseCommand
from halo.halo_api_client import HaloAPIClient

from help_desk_api.models import HelpDeskCreds


class Command(BaseCommand):
    help = "Get a ticket from Halo"  # /PS-IGNORE

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
            "-t", "--tickettypeid", type=int, help="Halo ticket type ID", required=True
        )
        parser.add_argument(
            "-o", "--output", type=pathlib.Path, help="Output file path (default: stdout)"
        )

    def handle(self, *args, **options):
        credentials = HelpDeskCreds.objects.get(zendesk_email=options["credentials"])
        self.halo_client = HaloAPIClient(
            client_id=credentials.halo_client_id, client_secret=credentials.halo_client_secret
        )

        ticket_type_id = options["tickettypeid"]

        ticket_type = self.get_halo_ticket_type(ticket_type_id)

        if options["output"]:
            output_path = options["output"].with_name(
                options["output"].name.format(
                    tickettypeid=ticket_type_id, timestamp=datetime.utcnow().isoformat()
                )
            )
            output_path = settings.BASE_DIR / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as output_file:
                json.dump(ticket_type, output_file, indent=4)
                print(f"Output written to {output_path}")
        else:
            json.dump(ticket_type, self.stdout, indent=4)

    def get_halo_ticket_type(self, ticket_type_id):
        ticket_type = self.halo_client.get(
            f"TicketType/{ticket_type_id}?includedetails=true&includelastaction=true"
        )
        return ticket_type