import json
import pathlib

import requests
from django.conf import settings
from django.core.management import BaseCommand

from help_desk_api.models import HelpDeskCreds


class Command(BaseCommand):
    help = "Get all Group records from the Zendesk API"  # /PS-IGNORE

    def __init__(self, stdout=None, stderr=None, **kwargs):
        super().__init__(stdout, stderr, **kwargs)

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument(
            "-zc",
            "--zendeskcreds",
            type=str,
            help="Email address for Zendesk credentials",
            nargs="?",
        )
        group.add_argument("-i", "--input", type=pathlib.Path, help="Input file path")
        parser.add_argument(
            "-hl", "--halocreds", type=pathlib.Path, help="Email address for Halo credentials"
        )
        parser.add_argument(
            "-o", "--output", type=pathlib.Path, help="Output file path (default: stdout)"
        )

    def handle(self, *args, **options):
        groups = None
        if options["zendeskcreds"]:
            # This means we try a real request to Zendesk
            groups = self.get_zendesk_data(options["zendeskcreds"])
        elif options["input"]:
            input_file_path = settings.BASE_DIR / options["input"]
            with open(input_file_path, "r") as input:
                groups = json.load(input)

        # make_halo_teams_from_zendesk_groups(options["halocreds"], groups)

        if options["output"]:
            output_path = settings.BASE_DIR / options["output"]
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as output_file:
                json.dump(groups, output_file, indent=4)
        # else:
        #     json.dump(groups, self.stdout, indent=4)

    def get_zendesk_data(self, credentials):
        credentials = HelpDeskCreds.objects.get(zendesk_email=credentials)
        # TODO: handle authorisation for Zendesk
        api_url = f"https://{credentials.zendesk_subdomain}.zendesk.com/api/v2/groups"
        response = requests.get(api_url)
        return response.json()
