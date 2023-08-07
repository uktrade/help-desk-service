import json
from datetime import datetime

from django.conf import settings

from help_desk_api.utils import ZenpyMacros

from .zendesk_data_base_command import ZendeskDataBaseCommand


class Command(ZendeskDataBaseCommand):
    help = "Extract macro templates from Zendesk JSON"  # /PS-IGNORE

    def handle(self, *args, **options):
        macro_data = self.load_zendesk_data(
            credentials=options["credentials"], file_path=options["inputfile"]
        )

        macros = ZenpyMacros(macro_data)

        content = {
            "plaintext_comments": macros.plaintext_comments,
            "html_comments": macros.html_comments,
            "subjects": macros.subjects,
        }

        if options["output"]:
            output_path = options["output"].with_name(
                options["output"].name.format(timestamp=datetime.utcnow().isoformat())
            )
            output_path = settings.BASE_DIR / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as output_file:
                json.dump(content, output_file, indent=4)
        else:
            json.dump(content, self.stdout, indent=4)
