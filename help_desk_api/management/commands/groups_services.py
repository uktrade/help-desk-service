import json
import pathlib

from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    help = "Compare Zendesk Groups v. Services"  # /PS-IGNORE

    groups_path = settings.BASE_DIR / "scripts/zendesk/zendesk_json/groups.json"
    services_path = settings.BASE_DIR / "scripts/zendesk/zendesk_json/services_field_options.json"

    def __init__(self, stdout=None, stderr=None, **kwargs):
        super().__init__(stdout, stderr, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            "-o", "--output", type=pathlib.Path, help="Output file path (default: stdout)"
        )

    def handle(self, *args, **options):
        with open(self.groups_path, "r") as input:
            groups = json.load(input)
        with open(self.services_path, "r") as input:
            services = json.load(input)

        group_names = {group["name"] for group in groups["groups"]}
        service_names = {service["name"] for service in services["custom_field_options"]}

        print("Groups:")  # /PS-IGNORE
        print(sorted(group_names))
        print("Services:")
        print(sorted(service_names))

        if options["output"]:
            output_path = settings.BASE_DIR / options["output"]
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as output_file:
                print("Groups:\n", file=output_file)
                for group_name in sorted(group_names):
                    print(group_name, file=output_file)
                print("\n", file=output_file)
                print("Services:\n", file=output_file)
                for service_name in sorted(service_names):
                    print(service_name, file=output_file)
        # print("Groups without services:")
        # groups_without_services = group_names - service_names
        # print(sorted(groups_without_services))
        #
        # print("Services without groups:")
        # services_without_groups = service_names - group_names
        # print(sorted(services_without_groups))
