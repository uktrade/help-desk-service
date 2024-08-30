import json
import pathlib
from datetime import datetime

import environ
from django.conf import settings
from django.core.management import BaseCommand
from email_router.ses_email_receiving.email_utils import (
    MicroserviceAPIClient,
    ParsedEmail,
)


class Command(BaseCommand):
    help = "Test"  # /PS-IGNORE

    def __init__(self, stdout=None, stderr=None, **kwargs):
        super().__init__(stdout, stderr, **kwargs)

    def add_arguments(self, parser):
        env = environ.Env()
        env.read_env()

        parser.add_argument(
            "-e",
            "--email",
            type=str,
            default=env.str("EMAIL_ROUTER_ZENDESK_EMAIL"),
            help="Zendesk user email address",
        )
        parser.add_argument(
            "-t",
            "--token",
            type=str,
            default=env.str("EMAIL_ROUTER_ZENDESK_TOKEN"),
            help="Zendesk API token",
        )

        parser.add_argument(
            "-i",
            "--input",
            type=pathlib.Path,
            default=pathlib.Path("email_router/tests/unit/fixtures/emails/plain-text-email.txt"),
            help="Input file path",
        )
        parser.add_argument(
            "-o", "--output", type=pathlib.Path, help="Output file path (default: stdout)"
        )

    def handle(self, *args, **options):
        input_email_path = options["input"].resolve()
        with open(input_email_path, "rb") as input_file:
            message = ParsedEmail(raw_bytes=input_file)

        client = MicroserviceAPIClient(
            zendesk_email=options["email"], zendesk_token=options["token"]
        )

        zendesk_response = client.create_or_update_ticket_from_message(message)

        # zendesk_response = self.create_ticket_from_message(message, options)
        #
        created_ticket = zendesk_response.ticket

        if options["output"]:
            output_path = options["output"].with_name(
                options["output"].name.format(
                    ticketid=created_ticket["ticket"]["id"], timestamp=datetime.utcnow().isoformat()
                )
            )
            output_path = settings.BASE_DIR / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as output_file:
                json.dump(created_ticket, output_file, indent=4)
                print(f"Output written to {output_path}")
        else:
            json.dump(created_ticket, self.stdout, indent=4)

        # groups = None
        # if options["zendeskcreds"]:
        #     # This means we try a real request to Zendesk
        #     groups = self.get_zendesk_data(options["zendeskcreds"])
        # elif options["input"]:
        #     input_file_path = settings.BASE_DIR / options["input"]
        #     with open(input_file_path, "r") as input:
        #         groups = json.load(input)
        #
        # # make_halo_teams_from_zendesk_groups(options["halocreds"], groups)
        #
        # if options["output"]:
        #     output_path = settings.BASE_DIR / options["output"]
        #     output_path.parent.mkdir(parents=True, exist_ok=True)
        #     with open(output_path, "w") as output_file:
        #         json.dump(groups, output_file, indent=4)
        # else:
        #     json.dump(groups, self.stdout, indent=4)

    # def get_zendesk_data(self, credentials):
    #     credentials = HelpDeskCreds.objects.get(zendesk_email=credentials)
    #     # TODO: handle authorisation for Zendesk
    #     api_url = f"https://{credentials.zendesk_subdomain}.zendesk.com/api/v2/groups"
    #     response = requests.get(api_url)
    #     return response.json()
