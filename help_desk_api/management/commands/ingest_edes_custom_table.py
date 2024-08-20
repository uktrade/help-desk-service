import json
import pathlib
import re
from datetime import datetime

from django.conf import settings
from django.core.management import BaseCommand

from help_desk_api.models import CustomField, Value


class Command(BaseCommand):
    help = "Ingest the values of the Halo custom table for EDES custom fields."  # /PS-IGNORE

    def __init__(self, stdout=None, stderr=None, **kwargs):
        super().__init__(stdout, stderr, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            "-i",
            "--input",
            type=pathlib.Path,
            help="Uktrade Zendesk  Service field JSON file path",
            required=True,
        )
        parser.add_argument(
            "-o", "--output", type=pathlib.Path, help="Output JSON file path (default: stdout)"
        )

    def handle(self, *args, **options):
        with open(options["input"], "r") as input_file:
            table_data = json.load(input_file)

        fields = table_data["ctfield"]["value"]
        value_matcher = re.compile(r".*, (?P<value>.+)$")

        value_mappings = [
            {
                "zendesk_value": value_matcher.search(field["display"]).group("value"),
                "halo_id": field["id"],
            }
            for field in fields
            if field["id"] > 1000
        ]

        known_ids = Value.objects.all().values_list("halo_id", flat=True)

        unknown_ids = [
            value_mapping
            for value_mapping in value_mappings
            if value_mapping["halo_id"] not in known_ids
        ]

        for value_mapping in unknown_ids:
            Value.objects.create(**value_mapping)

        output = unknown_ids

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

    def extract_service_field_values(self, service_field, halo_service_field):
        halo_values_by_name = {value["name"]: value["id"] for value in halo_service_field["values"]}
        values = {
            value["value"]: self.get_halo_id_by_zendesk_name(value["raw_name"], halo_values_by_name)
            for value in service_field["ticket_field"]["custom_field_options"]
        }

        return {
            "zendesk_name": service_field["ticket_field"]["raw_title"],
            "zendesk_id": service_field["ticket_field"]["id"],
            "halo_name": halo_service_field["name"],
            "halo_id": halo_service_field["id"],
            "is_multiselect": False,
            "value_mappings": dict(sorted(values.items())),
        }

    def get_halo_id_by_zendesk_name(self, zendesk_name, halo_values_by_name):
        try:
            halo_id = halo_values_by_name[zendesk_name]
        except KeyError:
            halo_name = self.name_exceptions[zendesk_name]
            halo_id = halo_values_by_name[halo_name]
        return halo_id

    name_exceptions = {
        "Datahub": "Data hub",
        "Check International Trade Barrier": "Check International Trade Barriers",
    }

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

    def map_zendesk_to_halo_values(self, zendesk_services, halo_service_field):
        pass
