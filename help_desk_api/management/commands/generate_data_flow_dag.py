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

    halo_json_spec_matcher = re.compile(
        r'^(?P<prefix>\s+)(?P<name>"[^"]+")(?P<middle>:\s+)((?P<is_string>"string")'
        r"|(?P<is_integer>0)|(?P<is_boolean>true)"
        r'|(?P<is_datetime>"2017-11-01T16:03:32.714Z"))(?P<eol>,?)$'
    )

    def transform_to_table_config(self, lines):
        def transformer(matches: re.Match):
            named_matches = matches.groupdict()
            type_matches = dict(filter(lambda kv: kv[0].startswith("is_"), named_matches.items()))
            try:
                type_match = next((key for key, value in type_matches.items() if value is not None))
            except StopIteration:
                return None
            type_info = ""
            match type_match:
                case "is_integer":
                    if named_matches.get("name", "") == '"id"':
                        type_info = "sa.BigInteger, primary_key=True"
                    else:
                        type_info = "sa.Integer"
                case "is_string":
                    type_info = "sa.String"
                case "is_boolean":
                    type_info = "sa.Boolean"
                case "is_datetime":
                    type_info = "sa.DateTime"
            return (
                f"{named_matches['prefix']}({named_matches['name']}, "
                f"sa.Column({named_matches['name']}, {type_info}))"
                f"{named_matches['eol']}"
            )

        transformed_lines = []
        for line in lines:
            transformed_line = self.halo_json_spec_matcher.sub(transformer, line)
            if transformed_line != line:
                transformed_lines.append(transformed_line)
        return "".join(transformed_lines)

    def handle(self, *args, **options):
        with open(options["input"], "r") as input_file:
            input_text = input_file.readlines()

        output_text = self.transform_to_table_config(input_text)

        if options["output"]:
            output_path = options["output"].with_name(
                options["output"].name.format(timestamp=datetime.utcnow().isoformat())
            )
            output_path = settings.BASE_DIR / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as output_file:
                print(output_text, file=output_file)
        else:
            print(output_text)
