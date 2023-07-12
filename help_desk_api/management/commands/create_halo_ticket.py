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
        parser.add_argument("-t", "--ticketid", type=int, help="Halo ticket ID", required=True)
        parser.add_argument(
            "-o", "--output", type=pathlib.Path, help="Output file path (default: stdout)"
        )

    def handle(self, *args, **options):
        credentials = HelpDeskCreds.objects.get(zendesk_email=options["credentials"])
        halo_client = HaloAPIClient(
            client_id=credentials.halo_client_id, client_secret=credentials.halo_client_secret
        )

        ticket_data = {
            "tickettype_id": 31,
            # "team": "Data Workspace",  # /PS-IGNORE
            "category_4": "Data Workspace",  # /PS-IGNORE
            # "ticket_tags": "once,upon,a time",  # /PS-IGNORE
            "summary": "Trying to work out what's happening to ticket_tags",
            "details": """Access request for

Username:   {username}
Journey:    {access_request.human_readable_journey}
Dataset:    {catalogue_item}
SSO Login:  {access_request.requester.email}
People search: {people_url}


Details for the request can be found at

{access_request_url}

""",  # /PS-IGNORE
            "userid": 44,  # my external email-related ID
        }

        response = halo_client.post(
            "Tickets", payload=[ticket_data]
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
        else:
            json.dump(response, self.stdout, indent=4)
