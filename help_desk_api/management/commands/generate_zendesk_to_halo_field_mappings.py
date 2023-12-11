import pathlib
from csv import DictReader
from datetime import datetime

from django.conf import settings
from django.core.management import BaseCommand
from django.template import Template
from django.template.loader import get_template

from help_desk_api.utils.field_mappings import ZendeskToHaloMapping


class Command(BaseCommand):
    help = "Associate Zendesk custom fields with Halo equivalents"  # /PS-IGNORE

    def __init__(self, stdout=None, stderr=None, **kwargs):
        super().__init__(stdout, stderr, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            "-i",
            "--input",
            type=pathlib.Path,
            help="Zendesk to Halo fields CSV file path",  # /PS-IGNORE
        )
        parser.add_argument(
            "-o", "--output", type=pathlib.Path, help="Output file path (default: stdout)"
        )

    def handle(self, *args, **options):
        with open(options["input"], "r") as input_file:
            reader = DictReader(input_file, restkey="ERROR-FIX-THIS")
            fields = list(reader)

        mappings = [ZendeskToHaloMapping(**field) for field in fields]
        mappings_by_zendesk_id = {
            f"'{field['zendesk_id']}'": ZendeskToHaloMapping(**field) for field in fields
        }

        context = {
            "mappings": mappings,
            "mappings_by_zendesk_id": mappings_by_zendesk_id,
        }
        template: Template = get_template("codegen/field_mappings.py.txt")
        output = template.render(context)

        if options["output"]:
            output_path = options["output"].with_name(
                options["output"].name.format(
                    timestamp=datetime.utcnow().isoformat(),
                )
            )
            output_path = settings.BASE_DIR / output_path
            with open(output_path, "w", encoding="utf-8-sig") as output_file:
                output_file.write(output)
        else:
            self.stdout.write(output)
