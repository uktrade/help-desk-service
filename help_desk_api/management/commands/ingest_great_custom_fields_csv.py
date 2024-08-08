import json
import pathlib
import re
from csv import DictReader
from datetime import datetime

from django.conf import settings
from django.core.management import BaseCommand

from help_desk_api.models import CustomField, Value


class Command(BaseCommand):
    help = "Create ticket on Zendesk by the same mechanism as email"  # /PS-IGNORE

    def __init__(self, stdout=None, stderr=None, **kwargs):
        super().__init__(stdout, stderr, **kwargs)
        self.dit_fields_by_id = None
        self.halo_fields = None
        self.halo_table = None
        self.halo_mappings = None
        self.halo_fields_by_sql = None

    def add_arguments(self, parser):
        parser.add_argument(
            "-c", "--countryfile", type=pathlib.Path, help="Countries JSON file path", required=True
        )
        parser.add_argument(
            "-s",
            "--sectorfile",
            type=pathlib.Path,
            help="Industry sectors JSON file path",
            required=True,
        )
        parser.add_argument(
            "-d",
            "--ditfields",
            type=pathlib.Path,
            help="DIT Zendesk fields JSON file path",
            required=True,
        )
        parser.add_argument(
            "-f", "--fields", type=pathlib.Path, help="Great fields CSV file path", required=True
        )
        parser.add_argument(
            "-t",
            "--halotable",
            type=pathlib.Path,
            help="Halo custom table JSON file path",
            required=True,
        )
        parser.add_argument(
            "-q",
            "--halofields",
            type=pathlib.Path,
            help="Halo fields JSON file path",
            required=True,
        )
        parser.add_argument(
            "-o", "--output", type=pathlib.Path, help="Output JSON file path (default: stdout)"
        )

    def normalise_name(self, name):
        return (
            name.lower()
            .replace(" ", "_")
            .replace("-", "_")
            .replace("(", "")
            .replace(")", "")
            .replace(",", "")
        )

    def get_country_values(self):
        return [
            f"{self.normalise_name(value['item'][0]['name'])}__ess_export"
            for _key, value in self.countries.items()
        ]

    def get_sector_values(self):
        return [f"{self.normalise_name(sector)}__ess_sector_l1" for sector in self.sectors]

    def dict_from_field(self, field):
        values = []
        try:
            values = [value for _key, value in json.loads(field["values"]).items()]
        except json.JSONDecodeError:
            if field["form field name"] == "markets":
                values = self.get_country_values()
            elif field["form field name"] == "sector_primary":
                values = self.get_sector_values()
        return {
            "zendesk_name": field["form field name"],
            "zendesk_id": field["zendesk field id"],
            "values": values,
            "is_multiselect": True,
        }

    countries = {}
    sectors = []

    countries_to_fix = (
        (" (Burma)", ""),
        ("Netherlands", "Netherland"),
    )
    countries_to_exclude = (
        "SU",
        "DD",
        "CS",
        "GB",
        "YU",
    )

    name_substitutions = {
        "closed_business__ess_organistations": "closed_business__ess_organistation",
        "tunisia__ess_export": "unisia__ess_export",
        "special_procedures_ess_dep_testing__use_a_customs_specila_procedure": "special_procedures_ess_dep_testing__use_a_customs_special_procedure",  # noqa: E501
        "special_procedures_ess_dep_testing__eligible_goods_and_authorise_uses": "special_procedures_ess_dep_testing__eligible__goods_and_authorised_uses",  # noqa: E501
        "exporting_samples_ess_dep_testing__understand_customs_declaration_when": "exporting_samples_ess_dep_testing__understand_customs_declaration_when_exporting_samples",  # noqa: E501
        "customs_declarations_ess_dep_testing__calculate_relevant_taxes_and_duties": "customs_declarations_ess_dep_testing__calculate_relevant_taxes__and_duties",  # noqa: E501
    }

    def handle(self, *args, **options):
        with open(options["fields"], "r", encoding="utf-8-sig") as csv_file:
            reader = DictReader(csv_file)
            great_fields = list(reader)

        with open(options["countryfile"], "r") as country_file:
            self.countries = json.load(country_file)
        self.fix_country_values()

        with open(options["sectorfile"], "r") as sector_file:
            self.sectors = json.load(sector_file)

        with open(options["halotable"], "r") as halo_table_file:
            self.halo_table = json.load(halo_table_file)

        with open(options["halofields"], "r", encoding="utf-8-sig") as f:
            self.halo_fields = json.load(f)

        with open(options["ditfields"], "r", encoding="utf-8-sig") as f:
            self.dit_fields = json.load(f)

        self.dit_fields_by_id = {
            str(field["id"]): field for field in self.dit_fields["ticket_fields"]
        }

        json_great_fields = {
            field["zendesk field id"]: self.dict_from_field(field)
            for field in great_fields
            if field["values"] != "String"
        }

        string_great_fields = {
            field["zendesk field id"]: {
                "zendesk_name": field["form field name"],
                "zendesk_id": field["zendesk field id"],
                "values": "",
                "is_multiselect": False,
            }
            for field in great_fields
            if field["values"] == "String"
        }

        self.halo_fields_by_sql = {
            self.field_lookup_name_from_sql(field["sqllookup"]).lower(): field["id"]
            for field in self.halo_fields
            if "sqllookup" in field and field["sqllookup"] and "CFEDESValue" in field["sqllookup"]
        }

        self.halo_fields_by_id = {field["id"]: field for field in self.halo_fields}

        self.halo_mappings = {
            value["customfields"][3]["value"]: {
                "id": value["id"],
                "field_id": self.halo_fields_by_sql[value["customfields"][1]["value"].lower()],
            }
            for value in self.halo_table["ctfield"]["value"]
        }

        halo_mappings, missing_halo_values = self.create_halo_field_mappings(json_great_fields)

        missing_zendesk_fields, missing_zendesk_values = self.check_field_values_in_zendesk_fields(
            json_great_fields
        )

        if missing_halo_values:
            self.stdout.write(f"Missing Halo values: {missing_halo_values}")
        if missing_zendesk_fields:
            self.stdout.write(f"Missing Zendesk fields: {missing_zendesk_fields}")
        if missing_zendesk_values:
            self.stdout.write(f"Missing Zendesk values: {missing_zendesk_values}")

        self.update_or_create_mappings(halo_mappings)

        all_fields = json_great_fields | string_great_fields

        output = {
            "missing_halo_values": missing_halo_values,
            "missing_zendesk_fields": missing_zendesk_fields,
            "missing_zendesk_values": missing_zendesk_values,
            "halo_mappings": halo_mappings,
            "all_fields": all_fields,
        }
        timestamp = datetime.utcnow().isoformat()

        if options["output"]:
            output_path = options["output"].with_name(
                options["output"].name.format(timestamp=timestamp)
            )
            output_path = settings.BASE_DIR / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as output_file:
                json.dump(output, output_file, indent=4)
                print(f"Output written to {output_path}")
        else:
            json.dump(output, self.stdout, indent=4)

    def update_or_create_mappings(self, halo_mappings):
        for zendesk_field_id, mapping in halo_mappings.items():
            values = []
            value_mappings = mapping.pop("value_mappings", {})
            for zendesk_value, halo_id in value_mappings.items():
                value, _created = Value.objects.update_or_create(
                    zendesk_value=zendesk_value, halo_id=halo_id
                )
                values.append(value)
            mapping["zendesk_id"] = int(zendesk_field_id)
            custom_field, created = CustomField.objects.update_or_create(**mapping)
            custom_field.values.set(values)
        return CustomField.objects.all()

    field_lookup_matcher = re.compile(r"'(.*)'")

    def field_lookup_name_from_sql(self, sql):
        match = self.field_lookup_matcher.search(sql)
        return match.group(1)

    def fix_country_values(self):
        for ex_country in self.countries_to_exclude:
            self.countries.pop(ex_country)
        for unwanted_value, replacement in self.countries_to_fix:
            for key, value in self.countries.items():
                if unwanted_value in value["item"][0]["name"]:
                    print(f"Found {unwanted_value}, replacing with {replacement}")
                    value["item"][0]["name"] = value["item"][0]["name"].replace(
                        unwanted_value, replacement
                    )

    def create_halo_field_mappings(self, fields):
        halo_mappings = {}
        missing_halo_mappings = []
        for field_id, values in fields.items():
            mapped_values = {}
            halo_field_id = None
            for value in values["values"]:
                if value in self.name_substitutions:
                    value = self.name_substitutions[value]
                try:
                    halo_id = self.halo_mappings[value]
                except KeyError:
                    missing_halo_mappings.append(f"{value} of {field_id} not in Halo table")
                    halo_id = {}
                mapped_values[value] = halo_id.get("id", None)
                if halo_field_id is None:
                    halo_field_id = halo_id.get("field_id", None)
                if halo_field_id != halo_id.get("field_id", halo_field_id):
                    raise ValueError(
                        f"Differing field IDs for same field's values: "
                        f"{halo_field_id} vs. {halo_id.get('field_id', None)}"
                    )
            halo_mappings[field_id] = {
                "zendesk_name": self.dit_fields_by_id[field_id]["title"],
                "halo_name": self.halo_fields_by_id[halo_field_id]["name"],
                "halo_id": halo_field_id,
                "value_mappings": mapped_values,
                "is_multiselect": values["is_multiselect"],
            }
        return halo_mappings, missing_halo_mappings

    def check_field_values_in_zendesk_fields(self, fields):
        dit_field_values = {
            str(field["id"]): [option["value"] for option in field["custom_field_options"]]
            for field in self.dit_fields["ticket_fields"]
            if "custom_field_options" in field
        }
        missing_zendesk_fields = []
        missing_zendesk_values = []
        for field_id, values in fields.items():
            if field_id not in dit_field_values:
                missing_zendesk_fields.append(
                    f"{field_id} ({fields[field_id]['zendesk_name']}) not found"
                )
                # raise KeyError()
            for value in values["values"]:
                if value not in dit_field_values[field_id]:
                    missing_zendesk_values.append(f"{value} for field {field_id} not found")
                    # raise KeyError()
        return missing_zendesk_fields, missing_zendesk_values
