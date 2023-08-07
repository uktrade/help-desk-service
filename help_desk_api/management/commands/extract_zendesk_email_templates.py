import json
from datetime import datetime

from django.conf import settings

from help_desk_api.utils import ZenpyTriggers

from .zendesk_data_base_command import ZendeskDataBaseCommand


class Command(ZendeskDataBaseCommand):
    help = "Extract email variable names from Zendesk JSON, e.g. triggers and macros"  # /PS-IGNORE

    def handle(self, *args, **options):
        trigger_data = self.load_zendesk_data(
            credentials=options["credentials"], file_path=options["inputfile"]
        )
        triggers = ZenpyTriggers(trigger_data)
        unique_emails = triggers.unique_emails

        if options["output"]:
            output_path = options["output"].with_name(
                options["output"].name.format(timestamp=datetime.utcnow().isoformat())
            )
            output_path = settings.BASE_DIR / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as output_file:
                json.dump(unique_emails, output_file, indent=4)
        else:
            json.dump(unique_emails, self.stdout, indent=4)
