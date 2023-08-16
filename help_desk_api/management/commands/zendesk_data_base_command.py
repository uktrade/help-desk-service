import argparse
import base64
import json
import pathlib

import requests
from django.core.management import BaseCommand

from help_desk_api.models import HelpDeskCreds


class ZendeskDataBaseCommand(BaseCommand):
    help = "Load data from either the Zendesk API or a JSON file"  # /PS-IGNORE
    api_response_content_field = None
    api_start_url_path = None

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
        datasources_group.add_argument(
            "-i", "--inputfile", type=pathlib.Path, help="Input file path"
        )
        parser.add_argument(
            "-o", "--output", type=pathlib.Path, help="Output file path (default: stdout)"
        )

    def handle(self, *args, **options):
        raise NotImplementedError("This command should be subclassed")

    def load_zendesk_data(self, token=None, credentials=None, file_path=None):
        if credentials:
            help_desk_creds = HelpDeskCreds.objects.get(zendesk_email=credentials)
            return self.fetch_api_data(token, help_desk_creds)
        else:
            return self.load_data_file(file_path)

    def fetch_api_data(self, token, help_desk_creds):
        # Use the Zendesk API to get data /PS-IGNORE
        # If it is in multiple pages, collapse them into the first page
        pages = list(
            self.api_pages(
                token=token, help_desk_creds=help_desk_creds, url_path=self.api_start_url_path
            )
        )
        first_page = pages[0]
        for page in pages[1:]:
            first_page[self.api_response_content_field] += page[self.api_response_content_field]
            first_page["count"] += page["count"]
        return first_page

    def api_pages(self, token, help_desk_creds: HelpDeskCreds, url_path):
        url = f"https://{help_desk_creds.zendesk_subdomain}.zendesk.com{url_path}"

        creds = f"{help_desk_creds.zendesk_email}/token:{token}"
        encoded_creds = base64.b64encode(creds.encode("ascii"))  # /PS-IGNORE

        while url:
            # Make request to Zendesk API
            zendesk_response = requests.get(
                url,
                headers={
                    "Authorization": f"Basic {encoded_creds.decode('ascii')}",  # /PS-IGNORE
                    "Content-Type": "application/json",
                },
            )
            content = zendesk_response.json()
            yield content
            url = content.get("next_page", None)

    def load_data_file(self, file_path):
        with open(file_path) as file:
            return json.load(file)
