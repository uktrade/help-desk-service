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
    halo_client = None
    existing_groups = {}

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
            "-m",
            "--macrofile",
            type=pathlib.Path,
            # required=True,
            help="Macros input file path",
        )

        parser.add_argument(
            "-o", "--output", type=pathlib.Path, help="Output file path (default: stdout)"
        )

    def handle(self, *args, **options):
        # extract email templates from triggers
        macro_contents = self.load_zendesk_macros(
            credentials=(options["credentials"], options["zendesktoken"]),
            macro_file_path=options["macrofile"],
        )
        macro_html = self.make_list_substitutions(items=macro_contents["html"])

        macro_text = self.make_list_substitutions(items=macro_contents["text"])
        htmlified_macro_text = self.htmlify(items=macro_text)

        macro_subjects = self.make_substitutions(items=macro_contents["subjects"])

        if options["credentials"]:
            help_desk_creds = HelpDeskCreds.objects.get(zendesk_email=options["credentials"])
            self.post_to_halo_canned_text(
                credentials=help_desk_creds,
                texts=macro_html,
                group="TEST: Zendesk HTML",  # /PS-IGNORE
            )
            self.post_to_halo_canned_text(
                credentials=help_desk_creds, texts=htmlified_macro_text, group="TEST: Zendesk text"
            )
            self.post_list_to_halo_canned_text(
                credentials=help_desk_creds, texts=macro_subjects, group="TEST: Zendesk subjects"
            )

        output = {
            "macro_subjects": macro_subjects,
            "macro_texts": htmlified_macro_text,
            "macro_html": macro_html,
        }

        if options["output"]:
            output_path = options["output"].with_name(
                options["output"].name.format(timestamp=datetime.utcnow().isoformat())
            )
            output_path = settings.BASE_DIR / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as output_file:
                json.dump(output, output_file, indent=4)
        else:
            json.dump(output, self.stdout, indent=4)

    def make_list_substitutions(self, items):
        for title, text_list in items.items():
            for index, text in enumerate(text_list):
                items[title][index] = self.mapper.map(text)
        return items

    def make_substitutions(self, items):
        return [self.mapper.map(text) for text in items]

    def htmlify(self, items):
        for title, text_list in items.items():
            for index, text in enumerate(text_list):
                items[title][index] = markdown(text)
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

    def load_zendesk_macros(self, credentials=None, macro_file_path=None):
        command_kwargs = self.get_command_kwargs(credentials, macro_file_path)
        call_command("extract_zendesk_macro_templates", **command_kwargs)
        return json.loads(command_kwargs["stdout"].getvalue())

    def post_to_halo_canned_text(
        self, credentials: HelpDeskCreds, texts, group="Default Group"  # /PS-IGNORE
    ):
        self.halo_client = HaloAPIClient(
            client_id=credentials.halo_client_id, client_secret=credentials.halo_client_secret
        )
        # canned text belongs to a group, so make sure the group exists
        group_id = self.ensure_group_exists(group)
        request_params = {
            "name": "",
            "group_id": group_id,
            "html": "",
        }

        for title, text_contents in texts.items():
            for index, text in enumerate(text_contents):
                if index:
                    suffix = f" ({index})"
                else:
                    suffix = ""
                request_params.update({"name": f"{title}{suffix}", "html": text})
                self.halo_client.post("CannedText", payload=[request_params])  # /PS-IGNORE

    def post_list_to_halo_canned_text(
        self, credentials: HelpDeskCreds, texts, group="Default Group"  # /PS-IGNORE
    ):
        self.halo_client = HaloAPIClient(
            client_id=credentials.halo_client_id, client_secret=credentials.halo_client_secret
        )
        # canned text belongs to a group, so make sure the group exists
        group_id = self.ensure_group_exists(group)
        request_params = {
            "name": "",
            "group_id": group_id,
            "html": "",
        }

        for text in texts:
            request_params.update({"name": text, "html": text})
            self.halo_client.post("CannedText", payload=[request_params])  # /PS-IGNORE

    def ensure_group_exists(self, group):
        if group in self.existing_groups:
            return self.existing_groups[group]["id"]
        path = "Lookup?showallcodes=true&lookupid=45"
        existing_groups = self.halo_client.get(path)
        for existing_group in existing_groups:
            if existing_group["name"] == group:
                self.existing_groups[group] = existing_group
                return existing_group["id"]
        # group does not exist, so create it
        params = {"lookupid": 45, "name": group}
        created_group = self.halo_client.post("Lookup", payload=[params])
        self.existing_groups[group] = created_group
        return created_group["id"]
