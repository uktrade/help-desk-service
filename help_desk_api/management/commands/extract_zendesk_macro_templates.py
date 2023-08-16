import json
from datetime import datetime

from django.conf import settings

from help_desk_api.utils import ZenpyMacros

from .zendesk_data_base_command import ZendeskDataBaseCommand


class Command(ZendeskDataBaseCommand):
    help = "Extract macro templates from Zendesk JSON"  # /PS-IGNORE
    api_response_content_field = "macros"
    api_start_url_path = "/api/v2/macros.json"

    def handle(self, *args, **options):
        macro_data = self.load_zendesk_data(
            token=options["zendesktoken"],
            credentials=options["credentials"],
            file_path=options["inputfile"],
        )

        macros = ZenpyMacros(macro_data)
        output = {
            "subjects": macros.subjects,
            "html": macros.with_html_comments,
            "text": macros.with_plaintext_comments,
        }

        if options["output"]:
            output_path = options["output"].with_name(
                options["output"].name.format(timestamp=datetime.utcnow().isoformat())
            )
            output_path = settings.BASE_DIR / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as output_file:
                json.dump(output, output_file, indent=4)
        else:
            json.dump(output, self.stdout, indent=4)
