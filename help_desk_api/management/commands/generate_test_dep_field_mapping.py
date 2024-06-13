import json
import pathlib
from datetime import datetime

from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = """
    Create mappings of Zendesk values for
     custom fields to Halo field value ids
    """  # /PS-IGNORE

    def __init__(self, stdout=None, stderr=None, **kwargs):
        super().__init__(stdout, stderr, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            "-c",
            "--customtable",
            type=pathlib.Path,
            help="Input file path for Halo custom table",
            required=True,
        )
        parser.add_argument(
            "-f",
            "--field",
            type=pathlib.Path,
            help="Input file path for Zendesk field",
            required=True,
        )
        parser.add_argument(
            "-o", "--output", type=pathlib.Path, help="Output file path (default: stdout)"
        )

    def handle(self, *args, **options):
        with open(options["customtable"], "r", encoding="utf-8-sig") as fp:
            custom_table = json.load(fp)
        with open(options["field"], "r", encoding="utf-8-sig") as fp:
            zendesk_field = json.load(fp)

        halo_ctfield_values = custom_table["ctfield"]["value"]
        zendesk_options = zendesk_field["ticket_field"]["custom_field_options"]

        halo_mappings_by_zendesk_value = {
            option["value"]: list(
                filter(
                    lambda v: v["customfields"][3]["value"].encode("ascii", "ignore").decode()
                    == option["value"].encode("ascii", "ignore").decode(),
                    halo_ctfield_values,
                )
            )[0]["id"]
            for option in sorted(zendesk_options, key=lambda o: o["value"])
        }

        output = halo_mappings_by_zendesk_value

        if options["output"]:
            output_path = options["output"].with_name(
                options["output"].name.format(timestamp=datetime.utcnow().isoformat())
            )
            output_path = settings.BASE_DIR / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as output_file:
                json.dump(output, output_file, indent=4)
                self.stdout.write(f"Written to {output_path}")
        else:
            json.dump(output, self.stdout, indent=4)

    def map_zendesk_options_to_halo_custom_table(self, zendesk_custom_field, halo_custom_table):
        zendesk_field_title = zendesk_custom_field["title"]
        zendesk_field_options = zendesk_custom_field["custom_field_options"]
        halo_custom_table_values = halo_custom_table["ctfield"]["value"]

        halo_values = [
            value["customfields"][3]
            for value in halo_custom_table_values
            if value["customfields"]["1"]["display"] == zendesk_field_title
        ]

        zendesk_values_to_halo_ids = {
            option["value"]: [
                halo_value for halo_value in halo_values if halo_value["value"] == option["value"]
            ][0]["id"]
            for option in sorted(zendesk_field_options, key=lambda option: option["value"])
        }
        return zendesk_values_to_halo_ids
