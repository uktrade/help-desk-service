import json
import pathlib
from datetime import datetime
from pprint import pprint

from django.conf import settings
from django.core.management import BaseCommand

from help_desk_api.utils.generated_field_mappings import halo_mappings_by_zendesk_id


class Command(BaseCommand):
    help = """
    Create mappings of Zendesk values for
     custom fields to Halo field value ids
    """  # /PS-IGNORE

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
            uktrade_fields = json.load(fp)
        with open(options["ditfields"], "r", encoding="utf-8-sig") as fp:
            dit_fields = json.load(fp)
        with open(options["halofields"], "r", encoding="utf-8-sig") as fp:
            halo_fields = json.load(fp)

        zendesk_fields_by_id = {}
        zendesk_fields_by_id.update(
            {
                uktrade_field["id"]: uktrade_field
                for uktrade_field in uktrade_fields["ticket_fields"]
            }
        )
        zendesk_fields_by_id.update(
            {dit_field["id"]: dit_field for dit_field in dit_fields["ticket_fields"]}
        )

        halo_fields_by_id = {halo_field["id"]: halo_field for halo_field in halo_fields}

        for field_id, mapping in halo_mappings_by_zendesk_id.items():
            if mapping.halo_id is None:
                continue
            zendesk_field = zendesk_fields_by_id[int(field_id)]
            if ("custom_field_options" in zendesk_field) and (
                field_options := zendesk_field["custom_field_options"]
            ):
                # print(f"ZF: {zendesk_field['title']}")
                halo_field = halo_fields_by_id[int(mapping.halo_id)]
                # print(f"HF: {halo_field['name']} ID: {halo_field['id']}")
                halo_field_values = halo_field.get("values", None)
                if halo_field_values is not None:
                    halo_field_values_by_title = {
                        halo_field_value["name"]: halo_field_value
                        for halo_field_value in halo_field_values
                    }
                    value_mappings = {}
                    for option in field_options:
                        zendesk_title = option["raw_name"]
                        try:
                            halo_value = halo_field_values_by_title[zendesk_title]
                            value_mappings[option["value"]] = halo_value["id"]
                        except KeyError:
                            self.stderr.write(
                                f"""
                                ZF: {zendesk_field['title']},
                                HF: {halo_field['name']}
                                ID: {halo_field['id']}, |{zendesk_title}|
                                """  # /PS-IGNORE
                            )
                    halo_mappings_by_zendesk_id[field_id].value_mappings = value_mappings
                else:
                    halo_mappings_by_zendesk_id[
                        field_id
                    ].value_mappings = f"TODO: {halo_field['sqllookup']}"

        # output = {
        #     zendesk_id: repr(mapping)
        #     for zendesk_id, mapping in halo_mappings_by_zendesk_id.items()
        # }
        output = halo_mappings_by_zendesk_id

        if options["output"]:
            output_path = options["output"].with_name(
                options["output"].name.format(timestamp=datetime.utcnow().isoformat())
            )
            output_path = settings.BASE_DIR / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as output_file:
                pprint(output, output_file)
                self.stdout.write(f"Written to {output_path}")
        else:
            json.dump(output, self.stdout, indent=4)
