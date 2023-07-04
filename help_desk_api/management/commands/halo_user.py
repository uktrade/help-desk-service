import json
import pathlib

from django.conf import settings
from django.core.management import BaseCommand
from halo.halo_api_client import HaloAPIClient

from help_desk_api.models import HelpDeskCreds


class Command(BaseCommand):
    help = "Get a User record from the Halo API"

    def __init__(self, stdout=None, stderr=None, **kwargs):
        super().__init__(stdout, stderr, **kwargs)
        self.credentials = HelpDeskCreds.objects.get(
            zendesk_email="halo-only@example.com"  # /PS-IGNORE
        )
        self.client = HaloAPIClient(
            self.credentials.halo_client_id, self.credentials.halo_client_secret
        )

    def add_arguments(self, parser):
        parser.add_argument(
            "userid", type=int, help="Halo ID of User", default=38, nargs="?"
        )  # Default: me! :-)
        parser.add_argument("-o", "--output", type=pathlib.Path)

    def handle(self, *args, **options):
        user_id = options["userid"]
        user_response = self.client.get(f"/Users/{user_id}")
        if options["output"]:
            output_path = settings.BASE_DIR / options["output"]
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as output_file:
                json.dump(user_response, output_file, indent=4)
        else:
            json.dump(user_response, self.stdout, indent=4)
