import json
import pathlib
from datetime import datetime

from django.conf import settings
from django.core.management import BaseCommand
from halo.halo_api_client import HaloAPIClient

from help_desk_api.models import HelpDeskCreds


class Command(BaseCommand):
    help = "Create user on Halo"  # /PS-IGNORE

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

        request_data = [
            {
                "name": f"Name-{datetime.utcnow().microsecond}",
                "emailaddress": f"x-{datetime.utcnow().microsecond}@example.com",  # /PS-IGNORE
                "other5": None,
                # "site_id": 1,
            }
        ]

        response = halo_client.post(
            "Users", payload=request_data
        )  # expects an array even for one user

        if options["output"]:
            output_path = options["output"].with_name(
                options["output"].name.format(
                    userid=response["id"], timestamp=datetime.utcnow().isoformat()
                )
            )
            output_path = settings.BASE_DIR / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as output_file:
                json.dump(response, output_file, indent=4)
                print(f"Output written to {output_path}")
        else:
            json.dump(response, self.stdout, indent=4)
