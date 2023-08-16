import json
import pathlib
import re
from datetime import datetime

from django.conf import settings
from django.core.management import BaseCommand


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
        variable_grabber = re.compile(r"\{\{([^}]+)")  # /PS-IGNORE

        with open(options["input"], "r") as input_file:
            input_text = input_file.read()

        variable_matches = variable_grabber.findall(input_text)
        unique_matches = dict(
            sorted(
                {
                    match: {
                        "zendesk_docs": "",
                        "halo_equivalent": "",
                    }
                    for match in set(variable_matches)
                }.items()
            )
        )

        if options["output"]:
            output_path = options["output"].with_name(
                options["output"].name.format(timestamp=datetime.utcnow().isoformat())
            )
            output_path = settings.BASE_DIR / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as output_file:
                json.dump(unique_matches, output_file, indent=4)
        else:
            json.dump(unique_matches, self.stdout, indent=4)
