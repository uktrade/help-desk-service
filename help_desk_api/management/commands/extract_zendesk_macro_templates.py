import json
import pathlib
from datetime import datetime

from django.conf import settings
from django.core.management import BaseCommand

from help_desk_api.utils import ZenpyMacros


class Command(BaseCommand):
    help = "Extract email variable names from Zendesk JSON, e.g. triggers and macros"  # /PS-IGNORE

    def __init__(self, stdout=None, stderr=None, **kwargs):
        super().__init__(stdout, stderr, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            "-i", "--input", type=pathlib.Path, required=True, help="Input file path"
        )
        parser.add_argument(
            "-o", "--output", type=pathlib.Path, help="Output file path (default: stdout)"
        )

    def handle(self, *args, **options):
        with open(options["input"], "r") as input_file:
            macros = json.load(input_file)

        macros = ZenpyMacros(macros)

        content = {
            "plaintext_comments": macros.plaintext_comments,
            "html_comments": macros.html_comments,
            "subjects": macros.subjects,
        }

        if options["output"]:
            output_path = options["output"].with_name(
                options["output"].name.format(timestamp=datetime.utcnow().isoformat())
            )
            output_path = settings.BASE_DIR / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as output_file:
                json.dump(content, output_file, indent=4)
        else:
            json.dump(content, self.stdout, indent=4)
