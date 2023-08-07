import argparse
import json
import pathlib

from django.core.management import BaseCommand


class ZendeskDataBaseCommand(BaseCommand):
    help = "Load data from either the Zendesk API or a JSON file"  # /PS-IGNORE

    def __init__(self, stdout=None, stderr=None, **kwargs):
        super().__init__(stdout, stderr, **kwargs)

    def add_arguments(self, parser: argparse.ArgumentParser):
        datasource_group = parser.add_mutually_exclusive_group(required=True)
        datasource_group.add_argument(
            "-c",
            "--credentials",
            type=str,
            help="Email address linked to Zendesk and Halo credentials",
        )
        datasource_group.add_argument(
            "-i", "--inputfile", type=pathlib.Path, help="Input file path"
        )
        parser.add_argument(
            "-o", "--output", type=pathlib.Path, help="Output file path (default: stdout)"
        )

    def handle(self, *args, **options):
        raise NotImplementedError("This command should be subclassed")

    def load_zendesk_data(self, credentials=None, file_path=None):
        if credentials:
            return self.fetch_api_data(credentials)
        else:
            return self.load_data_file(file_path)

    def fetch_api_data(self, credentials):
        # TODO: use the Zendesk API to get data /PS-IGNORE
        pass

    def load_data_file(self, file_path):
        with open(file_path) as file:
            return json.load(file)
