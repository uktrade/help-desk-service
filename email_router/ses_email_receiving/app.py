import json
import os
from datetime import datetime
from urllib.parse import unquote_plus

import boto3
from aws_lambda_powertools.utilities.data_classes import S3Event, event_source
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSEvent, SQSRecord

from .email_utils import APIClient, ParsedEmail

aws_session_token = os.environ.get("AWS_SESSION_TOKEN")  # /PS-IGNORE


@event_source(data_class=SQSEvent)
def lambda_handler(event: SQSEvent, context):
    iso_utcnow = get_iso_utcnow()
    parameters = get_parameters()

    api_client = APIClient(
        zendesk_email=parameters["ZENDESK_EMAIL"],
        zendesk_token=parameters["ZENDESK_TOKEN"],
        api_url=parameters["HELP_DESK_API_URL"],
    )

    emails = []
    s3_events = []
    bucket_name = ""
    record: SQSRecord
    for record in event.records:
        s3_event: S3Event = record.decoded_nested_s3_event
        s3_events.append(s3_event)
        bucket_name = s3_event.bucket_name
        object_key = unquote_plus(s3_event.object_key)
        email_content = get_email_from_bucket(bucket_name, object_key)
        parsed_email = ParsedEmail(raw_bytes=email_content)
        api_client.create_ticket_from_message(parsed_email)
        emails.append(parsed_email.subject)

    output_filename = f"lambda-output/incoming-{iso_utcnow}"

    status = {
        "statusCode": 200,
    }

    logged_output = {
        "status": status,
        "session_token": aws_session_token,
        "outputFilename": output_filename,
        "datetime": iso_utcnow,
        "emails": [str(email) for email in emails],
        "parameters": parameters,
        "event": event.raw_event,
        "s3_events": s3_events,
    }

    s3 = boto3.client("s3")
    s3.put_object(
        Bucket=bucket_name,
        Key=output_filename,
        Body=json.dumps(logged_output, indent=4),
    )
    return status


def get_email_from_bucket(bucket_name, object_key):
    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=bucket_name, Key=object_key)
    content = response["Body"]
    return content


def get_iso_utcnow():
    return datetime.utcnow().isoformat()


def get_parameters():
    ssm_client = boto3.client("ssm")
    parameters = {}
    for name in ["ZENDESK_EMAIL", "ZENDESK_TOKEN", "HELP_DESK_API_URL"]:
        parameter = ssm_client.get_parameter(Name=name, WithDecryption=True)
        parameters[name] = parameter["Parameter"]["Value"]  # /PS-IGNORE
    return parameters
