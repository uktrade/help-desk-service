import json
import pathlib
import re
from datetime import datetime

from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = """
    Create mappings of Zendesk values for
     custom fields to Halo field value ids
    """  # /PS-IGNORE

    UKTRADE_INCEPTION_DATE = "2016-09-09T17:36:48Z"
    DIT_INCEPTION_DATE = "2018-10-05T14:59:57Z"

    title_matcher = re.compile(r"[-\s?/()_]")

    custom_value_mappings = {
        "Service": {
            "Datahub": "Data hub",
            "Check International Trade Barrier": "Check International Trade Barriers",
        }
    }

    custom_field_name_mappings = {
        "Primary Location": "CFPrimaryLocationTagger",
        "Email": "CFemailAddress",
        "E Received From": "CFCFEReceivedFrom",
        "ESS MULTIS": "CFESSMultis",
        "ITA Name": "CFITA",
        "Route to Market": "CFRoutestoMarket",
        # "Enquiry ID Number": "CFEnquiryIDNumber",
        # "MA Barriers further information":
    }

    halo_names_by_lowercase = None
    halo_fields_by_name = None

    def __init__(self, stdout=None, stderr=None, **kwargs):
        super().__init__(stdout, stderr, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            "-d",
            "--ditfields",
            type=pathlib.Path,
            help="Input file path for dit.zendesk.com fields",
            required=True,
        )
        parser.add_argument(
            "-u",
            "--uktradefields",
            type=pathlib.Path,
            help="Input file path for uktrade.zendesk.com fields",
            required=True,
        )
        parser.add_argument(
            "-t",
            "--halofields",
            type=pathlib.Path,
            help="Input file path for Halo fields",
            required=True,
        )
        parser.add_argument(
            "-o", "--output", type=pathlib.Path, help="Output file path (default: stdout)"
        )

    def handle(self, *args, **options):
        with open(options["uktradefields"], "r", encoding="utf-8-sig") as fp:
            uktrade_zendesk_fields = json.load(fp)["ticket_fields"]
        with open(options["ditfields"], "r", encoding="utf-8-sig") as fp:
            dit_zendesk_fields = json.load(fp)["ticket_fields"]
        with open(options["halofields"], "r", encoding="utf-8-sig") as fp:
            halo_fields = json.load(fp)

        uktrade_custom_fields = [
            field
            for field in uktrade_zendesk_fields
            if not self.is_original_zendesk_field(field["created_at"], self.UKTRADE_INCEPTION_DATE)
        ]
        dit_custom_fields = [
            field
            for field in dit_zendesk_fields
            if not self.is_original_zendesk_field(field["created_at"], self.DIT_INCEPTION_DATE)
        ]

        zendesk_custom_fields = uktrade_custom_fields + dit_custom_fields
        zendesk_to_halo_fields = self.map_zendesk_ids_to_halo_fields(
            zendesk_custom_fields, halo_fields
        )

        output = zendesk_to_halo_fields

        if options["output"]:
            # -o temp_data/z-h/zendesk_to_halo_custom_field_mappings-{timestamp}.py
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

    def map_zendesk_ids_to_halo_fields(
        self,
        zendesk_custom_fields,
        halo_fields,
    ):
        self.halo_fields_by_name = {halo_field["name"]: halo_field for halo_field in halo_fields}
        self.halo_names_by_lowercase = {key.lower(): key for key in self.halo_fields_by_name.keys()}
        mappings = {}
        equivalent_halo_field_not_found = []
        zendesk_options_not_found = []
        halo_values_not_found = []
        missing_option_to_value_mappings = {}
        for field in zendesk_custom_fields:
            zendesk_title = field["title"]
            halo_name = self.custom_field_name_mappings.get(zendesk_title)
            if halo_name is None:
                lowercase_halo_name = self.halo_name_from_zendesk_title(zendesk_title).lower()
                if lowercase_halo_name not in self.halo_names_by_lowercase:
                    equivalent_halo_field_not_found.append([zendesk_title, field["id"]])
                    self.stdout.write(
                        f"{zendesk_title}: {field['id']} "
                        f"equivalent not found for {lowercase_halo_name}"
                    )
                    continue
                halo_name = self.halo_names_by_lowercase[lowercase_halo_name]
            halo_field = self.halo_fields_by_name[halo_name]
            custom_field_options = field.get("custom_field_options")
            if custom_field_options is None:
                zendesk_options_not_found.append(zendesk_title)
                self.stdout.write(
                    f"Zendesk field {zendesk_title} does not have custom field options"
                )
                continue
            halo_values = halo_field.get("values")
            if halo_values is None:
                halo_values_not_found.append(halo_name)
                self.stdout.write(f"Halo field {halo_name} does not have values")
                continue
            mapped_values, missing_values = self.map_options_to_values(
                custom_field_options, halo_values, zendesk_title
            )
            if missing_values:
                if zendesk_title in missing_option_to_value_mappings:
                    missing_values = (
                        missing_option_to_value_mappings[zendesk_title] + missing_values
                    )
                missing_option_to_value_mappings[zendesk_title] = missing_values
            mappings[field["id"]] = mapped_values
        return {
            "equivalent_halo_field_not_found": equivalent_halo_field_not_found,
            "zendesk_options_not_found": zendesk_options_not_found,
            "halo_values_not_found": halo_values_not_found,
            "missing_option_to_value_mappings": missing_option_to_value_mappings,
            "mappings": mappings,
        }

    def map_options_to_values(self, options, values, zendesk_title):
        value_mappings = {}
        missing_mappings = []
        for option in options:
            option_name = option["raw_name"]
            halo_value = [value for value in values if value["name"] == option_name]
            if not halo_value:
                custom_mappings = self.custom_value_mappings.get(zendesk_title, {})
                halo_value = custom_mappings.get(option_name)
            if halo_value:
                value_mappings[option_name] = halo_value
            else:
                option_value = option["value"]
                missing_mappings.append([option_name, option_value])
                self.stdout.write(
                    f"Zendesk option {option_name} "
                    f"(value {option_value}) does not have a Halo value"
                )
                continue
        return value_mappings, missing_mappings

    def create_zendesk_to_halo_mapping(self):
        pass

    def halo_name_from_zendesk_title(self, zendesk_title):
        halo_name = f"CF{self.title_matcher.sub('', zendesk_title)}"
        if halo_name.startswith("CFESS"):
            halo_name = re.sub(r"^CFESS", "CFEDES", halo_name)
        return halo_name

    def is_original_zendesk_field(self, creation_date, inception_date=UKTRADE_INCEPTION_DATE):
        return creation_date == inception_date

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
