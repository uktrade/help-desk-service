import argparse
import json
import pathlib
from datetime import datetime
from io import StringIO

from django.conf import settings
from django.core.management import BaseCommand, call_command
from halo.halo_api_client import HaloAPIClient
from markdown import markdown

from help_desk_api.models import HelpDeskCreds
from help_desk_api.utils import PlaceholderMapper


class Command(BaseCommand):
    help = "Check piping from one command to another"  # /PS-IGNORE
    mapper = PlaceholderMapper()

    def __init__(self, stdout=None, stderr=None, **kwargs):
        super().__init__(stdout, stderr, **kwargs)

    def add_arguments(self, parser: argparse.ArgumentParser):
        datasources_group = parser.add_mutually_exclusive_group()
        credentials_group = datasources_group.add_argument_group(
            title="Credentials for querying Zendesk API"  # /PS-IGNORE
        )
        credentials_group.add_argument(
            "-c",
            "--credentials",
            type=str,
            help="Email address linked to Zendesk and Halo credentials",
        )
        credentials_group.add_argument(
            "-z",
            "--zendesktoken",
            type=str,
            help="Zendesk token",
        )

        input_files_group = datasources_group.add_argument_group(
            title="Input JSON files",
            description="If no API credentials given, "
            "specify JSON files containing the data",  # /PS-IGNORE
        )
        input_files_group.add_argument(
            "-t",
            "--triggerfile",
            type=pathlib.Path,
            # required=True,
            help="Triggers input file path",
        )

        parser.add_argument(
            "-o", "--output", type=pathlib.Path, help="Output file path (default: stdout)"
        )

    def handle(self, *args, **options):
        # extract email templates from triggers
        trigger_emails = self.load_zendesk_triggers(
            credentials=(options["credentials"], options["zendesktoken"]),
            trigger_file_path=options["triggerfile"],
        )
        substituted_trigger_emails = self.make_substitutions(
            items=trigger_emails, fields=["subject", "body"]
        )
        htmlified_trigger_emails = self.htmlify(items=substituted_trigger_emails, fields=["body"])

        if options["credentials"]:
            help_desk_creds = HelpDeskCreds.objects.get(zendesk_email=options["credentials"])
            self.post_to_halo_email_templates(
                credentials=help_desk_creds, emails=htmlified_trigger_emails
            )

        if options["output"]:
            output_path = options["output"].with_name(
                options["output"].name.format(timestamp=datetime.utcnow().isoformat())
            )
            output_path = settings.BASE_DIR / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as output_file:
                json.dump(trigger_emails, output_file, indent=4)
        else:
            json.dump(trigger_emails, self.stdout, indent=4)

    def make_substitutions(self, items, fields):
        for item in items:
            for field in fields:
                item[field] = self.mapper.map(item[field])
        return items

    def htmlify(self, items, fields):
        for item in items:
            for field in fields:
                item[field] = markdown(item[field])
        return items

    def get_command_kwargs(self, credentials, data_file_path):
        command_kwargs = {
            "stdout": StringIO(),
        }
        if data_file_path:
            command_kwargs.update({"inputfile": data_file_path})
        else:
            api_credentials, zendesk_token = credentials
            command_kwargs.update({"credentials": api_credentials, "zendesktoken": zendesk_token})
        return command_kwargs

    def load_zendesk_triggers(self, credentials=None, trigger_file_path=None):
        command_kwargs = self.get_command_kwargs(credentials, trigger_file_path)
        call_command("extract_zendesk_email_templates", **command_kwargs)
        return json.loads(command_kwargs["stdout"].getvalue())

    def post_to_halo_email_templates(self, credentials: HelpDeskCreds, emails):
        # emails = emails[0:20]  # TODO: remove this, it's just for development
        halo_request_email_bodies = [
            {"name": email["title"], "header_text": email["subject"], "body_html": email["body"]}
            for email in emails
        ]
        halo_client = HaloAPIClient(
            client_id=credentials.halo_client_id, client_secret=credentials.halo_client_secret
        )
        for email in halo_request_email_bodies:
            """
            Although the endpoint accepting an array might lead you to believe that
            multiple templates could be posted as a batch, it turns out Halo doesn't
            expect that, and all kinds of strange data corruption occurs.
            So we have to do them one by one.
            """
            halo_client.post(path="EmailTemplate", payload=[email])  # /PS-IGNORE
