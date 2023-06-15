import json
import pathlib

import requests
from django.conf import settings
from django.core.management import BaseCommand
from django.urls import reverse

from help_desk_api.models import HelpDeskCreds


class Command(BaseCommand):
    help = "Get a User record from the Zendesk API"

    def __init__(self, stdout=None, stderr=None, **kwargs):
        super().__init__(stdout, stderr, **kwargs)
        self.credentials = HelpDeskCreds.objects.get(
            zendesk_email="halo-only@example.com"  # /PS-IGNORE
        )

    def add_arguments(self, parser):
        parser.add_argument(
            "userid", type=int, help="Halo ID of User", default=38, nargs="?"
        )  # Default: me! :-)
        parser.add_argument("-o", "--output", type=pathlib.Path)

    def handle(self, *args, **options):
        user_id = options["userid"]
        user_url = reverse("api:user", kwargs={"id": user_id})
        api_url = f"https://{self.credentials.subdomain}.zendesk.com{user_url}"
        user_response = requests.get(api_url)
        if options["output"]:
            output_path = settings.BASE_DIR / options["output"]
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as output_file:
                json.dump(user_response, output_file, indent=4)
        else:
            json.dump(user_response, self.stdout, indent=4)
