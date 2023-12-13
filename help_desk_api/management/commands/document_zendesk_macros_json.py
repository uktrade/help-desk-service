import csv
import json
import pathlib
from csv import DictWriter
from datetime import datetime

from django.conf import settings
from django.core.management import BaseCommand

from help_desk_api.utils import ZendeskMacros


class Command(BaseCommand):
    help = "Document triggers from Zendesk JSON"  # /PS-IGNORE

    def __init__(self, stdout=None, stderr=None, **kwargs):
        super().__init__(stdout, stderr, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            "-i", "--input", type=pathlib.Path, required=True, help="Input file path"
        )
        parser.add_argument(
            "-f", "--fields", type=pathlib.Path, help="Zendesk fields JSON file path"
        )
        parser.add_argument(
            "-g", "--groups", type=pathlib.Path, help="Zendesk groups JSON file path"
        )
        parser.add_argument("-p", "--prefix", type=str, help="Zendesk instance", default="uktrade")
        parser.add_argument(
            "-o", "--output", type=pathlib.Path, help="Output file path (default: stdout)"
        )

    def handle(self, *args, **options):
        with open(options["input"], "r") as input_file:
            triggers = json.load(input_file)

        groups = {}
        if options["groups"]:
            groups = self.load_groups(options["groups"])

        fields = {}
        if options["fields"]:
            fields = self.load_fields(options["fields"])

        zendesk_config = {"groups": groups, "fields": fields, "instance": options["prefix"]}

        triggers = ZendeskMacros(triggers, zendesk_config)
        context = triggers.document()

        output = [
            {
                "title": item["title"],
                "description": item["description"],
                "action_label": action["label"],
                "action_raw_action": action["raw_action"],
                "action_value": action["value"],
                "action_help": action["help"].strip(),
            }
            for item in context["items"]
            for action in item["actions"]
        ]

        if options["output"]:
            output_path = options["output"].with_name(
                options["output"].name.format(timestamp=datetime.utcnow().isoformat())
            )
            output_path = settings.BASE_DIR / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8-sig") as output_file:
                writer = DictWriter(output_file, output[0].keys(), dialect=csv.excel)
                writer.writeheader()
                for item in output:
                    writer.writerow(item)
        else:
            writer = DictWriter(self.stdout, output[0].keys(), dialect=csv.excel)
            writer.writeheader()
            for item in output:
                writer.writerow(item)

    def load_groups(self, groups_file_path):
        with open(groups_file_path, "r") as groups_file:
            groups_data = json.load(groups_file)
        groups = {
            str(group["id"]): group["name"]
            for group in groups_data["groups"]
            if group["deleted"] is False
        }
        return groups

    def load_fields(self, fields_file_path):
        with open(fields_file_path, "r") as fields_file:
            fields_data = json.load(fields_file)
        fields = {
            str(field["id"]): field["raw_title"] if field["raw_title"] else field["title"]
            for field in fields_data["ticket_fields"]
        }
        return fields
