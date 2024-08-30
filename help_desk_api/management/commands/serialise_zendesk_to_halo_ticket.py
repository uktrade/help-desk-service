import json
import pathlib
from datetime import datetime

from django.conf import settings
from django.core.cache import caches
from django.core.management import BaseCommand

from help_desk_api.serializers import ZendeskToHaloCreateTicketSerializer


class Command(BaseCommand):
    help = "Create ticket on Halo using EDES Zendesk ticket data"  # /PS-IGNORE

    groups_path = settings.BASE_DIR / "scripts/zendesk/zendesk_json/groups.json"
    services_path = settings.BASE_DIR / "scripts/zendesk/zendesk_json/services_field_options.json"

    def add_arguments(self, parser):
        parser.add_argument(
            "-i", "--input", type=pathlib.Path, required=True, help="Input file path"
        )
        parser.add_argument(
            "-o", "--output", type=pathlib.Path, help="Output file path (default: stdout)"
        )

    def handle(self, *args, **options):

        with open(options["input"], "r") as fp:
            ticket_data = json.load(fp)

        cache = caches[settings.USER_DATA_CACHE]
        requester_id = ticket_data["ticket"]["requester_id"]
        cache.set(
            requester_id,
            {
                "user": {
                    "name": "Some Body",
                    "email": "some.body@example.com",  # /PS-IGNORE
                }
            },
        )

        serialiser = ZendeskToHaloCreateTicketSerializer()
        output = serialiser.to_representation(ticket_data["ticket"])

        if options["output"]:
            output_path = options["output"].with_name(
                options["output"].name.format(timestamp=datetime.utcnow().isoformat())
            )
            output_path = settings.BASE_DIR / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as output_file:
                json.dump(output, output_file, indent=4)
                print(f"Output written to {output_path}")
        else:
            json.dump(output, self.stdout, indent=4)
