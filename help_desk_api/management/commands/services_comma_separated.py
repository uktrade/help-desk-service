import json
import pathlib

from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "Get services and write to CSV file"  # /PS-IGNORE

    groups_path = settings.BASE_DIR / "scripts/zendesk/zendesk_json/groups.json"
    services_path = settings.BASE_DIR / "scripts/zendesk/zendesk_json/services_field_options.json"

    def __init__(self, stdout=None, stderr=None, **kwargs):
        super().__init__(stdout, stderr, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            "-o", "--output", type=pathlib.Path, help="Output file path (default: stdout)"
        )

    def handle(self, *args, **options):
        with open(self.services_path, "r") as input:
            services = json.load(input)

        service_names = {service["name"] for service in services["custom_field_options"]}

        if options["output"]:
            output_path = settings.BASE_DIR / options["output"]
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as output_file:
                for service_name in sorted(service_names):
                    print(f"{service_name},", file=output_file, end="")
        # print("Groups without services:")
        # groups_without_services = group_names - service_names
        # print(sorted(groups_without_services))
        #
        # print("Services without groups:")
        # services_without_groups = service_names - group_names
        # print(sorted(services_without_groups))
