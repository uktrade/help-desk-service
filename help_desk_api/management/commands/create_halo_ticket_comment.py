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

        search_term = "some.body@example.com"  # /PS-IGNORE

        user_search_result = halo_client.get(f"users?search={search_term}")
        user = user_search_result["users"][0]

        user_id = user["id"]
        user_name = user["name"]

        halo_comment_data = {
            "ticket_id": 9688,
            "note_html": f"<div dir='ltr'>Supplier test reply via script "
            f"at {datetime.utcnow().isoformat()}</div>",
            "hiddenfromuser": True,
            "user_id": user_id,
            "emailfrom": search_term,
            "who": user_name,
            "supplier_id": 6,
            "outcome_id": 79,
        }

        response = halo_client.post(
            "Actions", payload=[halo_comment_data]
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
