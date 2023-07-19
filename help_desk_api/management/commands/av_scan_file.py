from django.conf import settings
from django.core.management import BaseCommand
from halo.clam_av import (
    CLAM_AV_HOST,
    CLAM_AV_PATH,
    av_scan_file,
    check_av_service,
    skip_file_extension,
)


class Command(BaseCommand):
    help = "Scan a file for viruses"

    def __init__(self, stdout=None, stderr=None, **kwargs):
        super().__init__(stdout, stderr, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            "-f",
            "--filename",
            type=str,
            help="File to be scanned for viruses",
            required=True,
        )

    def handle(self, *args, **kwargs):
        filename = kwargs["filename"]
        path = settings.BASE_DIR / f"tests/help_desk_api/{filename}"
        if not skip_file_extension(path):
            if check_av_service(CLAM_AV_HOST, CLAM_AV_PATH) == "OK":
                if av_scan_file(path) == "OK":
                    print("proceed to Uploading the file")
