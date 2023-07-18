import json
import logging
import pathlib
from base64 import b64encode
import requests
import json
from http.client import HTTPConnection

from django.conf import settings

logger = logging.getLogger(__name__)

# Clam AV
CLAM_AV_USERNAME = settings.CLAM_AV_USERNAME
CLAM_AV_PASSWORD = settings.CLAM_AV_PASSWORD
CLAM_AV_URL = settings.CLAM_AV_URL
CLAM_AV_HOST = settings.CLAM_AV_HOST

CLAM_AV_PATH = "/"

# Add/remove file extensions for files that you do not want to scan
CLAM_AV_IGNORE_EXTENSIONS = [".png", ".pdf"]


class AntiVirusServiceErrorException(Exception):
    pass

class MalformedAntiVirusResponseException(Exception):
    pass


# Check file extension and skip files with certain extension
def skip_file_extension(file_name):
    extension = pathlib.Path(file_name).suffix

    if extension in CLAM_AV_IGNORE_EXTENSIONS:
        return True
    else:
        return False


# Prior to accessing clam_av service check that service is reachable
# Makes a GET request to the av host endpoint
def check_av_service(CLAM_AV_HOST, CLAM_AV_PATH):
    response = requests.get(f"http://{CLAM_AV_HOST}/{CLAM_AV_PATH}")
    if response.status_code == 200:
        return "OK"
    else:
        return "NOT OK"
    


def av_scan_file(file_name):
    '''
    Function that POSTs a file to av service for scanning
    '''
    credentials = b64encode(
        bytes(
            f"{CLAM_AV_USERNAME}:{CLAM_AV_PASSWORD}",
            encoding="utf8",
        )
    ).decode("ascii")

    response = requests.post(
        CLAM_AV_URL,
        headers={
            "Authorization": f"Basic {credentials}",
        },
        files={"file": open(file_name, "rb")}
    )

    av_results = response.json()

    if "malware" not in av_results:
        msg = "Malformed response from AV server"
        logger.warning(msg)
        av_passed = False
        av_reason = msg

        raise MalformedAntiVirusResponseException()

    if av_results["malware"]:
        av_passed = False
        av_reason = av_results["reason"]
        msg = f"Malware found in user uploaded file {file_name}, exiting upload process"
        logger.warning(msg)
        av_passed = False
    else:
        av_passed = True

    return av_passed


if __name__ == "__main__":
    FILENAME = "/Users/nikosbaltas/uktrade_dev/help-desk-service/tests/help_desk_api/eicar.txt"
    if not skip_file_extension(FILENAME):
        if check_av_service(CLAM_AV_HOST, CLAM_AV_PATH) == "OK":
            if av_scan_file(FILENAME) == 'OK':
                print("proceed to Uploading the file")
