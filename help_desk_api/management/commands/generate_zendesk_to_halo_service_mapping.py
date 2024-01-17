import json
import pathlib
from datetime import datetime

from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = """
    Create mappings of Zendesk values for
     Service custom field to Halo CFService field id values
    """  # /PS-IGNORE

    def __init__(self, stdout=None, stderr=None, **kwargs):
        super().__init__(stdout, stderr, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            "-d",
            "--ditfield",
            type=pathlib.Path,
            help="Input file path for dit.zendesk.com field",
            required=True,
        )
        parser.add_argument(
            "-u",
            "--uktradefield",
            type=pathlib.Path,
            help="Input file path for uktrade.zendesk.com field",
            required=True,
        )
        parser.add_argument(
            "-t",
            "--halofield",
            type=pathlib.Path,
            help="Input file path for Halo field",
            required=True,
        )
        parser.add_argument(
            "-o", "--output", type=pathlib.Path, help="Output file path (default: stdout)"
        )

    def handle(self, *args, **options):
        with open(options["uktradefield"], "r", encoding="utf-8-sig") as fp:
            uktrade_field = json.load(fp)
        with open(options["ditfield"], "r", encoding="utf-8-sig") as fp:
            dit_field = json.load(fp)
        with open(options["halofield"], "r", encoding="utf-8-sig") as fp:
            halo_field = json.load(fp)

        uktrade_services = {
            option["value"]: option["raw_name"] for option in uktrade_field["custom_field_options"]
        }

        dit_services = {
            option["value"]: option["raw_name"] for option in dit_field["custom_field_options"]
        }

        halo_services = {value["name"]: value["id"] for value in halo_field["values"]}

        services_to_halo_ids = {}

        for value, name in uktrade_services.items():
            if value not in services_to_halo_ids:
                services_to_halo_ids[value] = halo_services[name]
            else:
                self.stdout.write(f"{value} already in there")

        for value, name in dit_services.items():
            if value not in services_to_halo_ids:
                services_to_halo_ids[value] = halo_services[name]
            else:
                self.stdout.write(f"{value} already in there")

        output = services_to_halo_ids

        if options["output"]:
            output_path = options["output"].with_name(
                options["output"].name.format(timestamp=datetime.utcnow().isoformat())
            )
            output_path = settings.BASE_DIR / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as output_file:
                output_dict_as_str = json.dumps(output, indent=4)
                output_file.write(f"service_names_to_ids = {output_dict_as_str}")
        else:
            json.dump(output, self.stdout, indent=4)
