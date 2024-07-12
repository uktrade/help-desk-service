import json
import os
from datetime import datetime
from http import HTTPStatus
from json import JSONDecodeError
from urllib.parse import unquote_plus

import boto3
from aws_lambda_powertools.logging.logger import Logger
from aws_lambda_powertools.utilities.data_classes import S3Event, event_source
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSEvent, SQSRecord
from aws_lambda_powertools.utilities.typing import LambdaContext
from botocore.exceptions import ClientError
from email_utils import HaloAPIClient, MicroserviceAPIClient, ParsedEmail
from requests import HTTPError

logger: Logger = Logger()
logger.setLevel("DEBUG" if os.environ.get("DEBUG", False) else "INFO")

aws_session_token = os.environ.get("AWS_SESSION_TOKEN")  # /PS-IGNORE

USE_MICROSERVICE_DEFAULT = True

STATUS_OK = {
    "statusCode": HTTPStatus.OK,
}


@event_source(data_class=SQSEvent)
def lambda_handler(event: SQSEvent, context: LambdaContext):
    """
    Note: values written to the S3 bucket are for logging and debugging purposes
    and that code will be removed when the function is deemed stable.
    """
    iso_utcnow = get_iso_utcnow()
    parameters = get_parameters()

    logger.info("Lambda invocation")

    s3 = boto3.client("s3")
    record_type = get_raw_record_type(event)
    if record_type == "s3:TestEvent":  # /PS-IGNORE
        logger.warning("S3 TestEvent: discarding")
        bucket_name = "dbt-help-desk-incoming-mail"
        s3.put_object(
            Bucket=bucket_name,
            Key=f"tempdebug/event-{iso_utcnow}",
            Body=json.dumps(event.raw_event, indent=4),
        )
        return STATUS_OK

    api_client = get_configured_api_client(parameters)

    emails = []
    bucket_name = ""
    record: SQSRecord
    for record in event.records:
        try:
            s3_event: S3Event = record.decoded_nested_s3_event
        except JSONDecodeError:
            # This can happen with things like SQS test events sent at initialisation  /PS-IGNORE
            logger.warning(
                "S3Event JSONDecodeError",
                extra={
                    "raw_event": event.raw_event,
                },
            )
            continue
        logger.debug(
            "Event decoded",
            extra={
                "raw_event": event.raw_event,
            },
        )
        bucket_name = s3_event.bucket_name
        object_key = unquote_plus(s3_event.object_key)
        try:
            email_content = get_email_from_bucket(s3, bucket_name, object_key)
        except ClientError:
            # This happens if access is denied, e.g. if the object has been deleted
            # If we ignore it, the queue message will then be discarded
            logger.warning(
                "ClientError retrieving S3 object",
                extra={
                    "bucket_name": bucket_name,
                    "object_key": object_key,
                },
            )
            continue
        parsed_email = ParsedEmail(raw_bytes=email_content)
        try:
            logger.info("Creating or updating ticket")
            api_client.create_or_update_ticket_from_message(parsed_email)
        except HTTPError as e:
            logger.error(
                "HTTPError in lambda_handler", extra={"response_content": e.response.content}
            )
            raise
        except AttributeError:
            logger.warning(
                "AttributeError for email",
                extra={
                    "bucket_name": bucket_name,
                    "object_key": object_key,
                },
            )
        emails.append(parsed_email.subject)

    status = STATUS_OK

    save_debug_data_to_s3(s3, bucket_name, emails, event, iso_utcnow, parameters, status)
    return status


def remove_email_from_bucket(s3, bucket_name, object_key, destination_bucket):
    logger.log("Removing mail from bucket")


def get_raw_record_type(event):
    raw_records = event.raw_event.get("Records", [])
    first_record = raw_records[0] if raw_records else {}
    record_body = json.loads(first_record.get("body", "{}"))
    record_type = record_body.get("Event", None)
    return record_type


def get_configured_api_client(parameters):
    use_microservice = os.environ.get("USE_MICROSERVICE", USE_MICROSERVICE_DEFAULT)
    if use_microservice:
        logger.info("Using Microservice API (Zendesk compatible)")
        api_client = MicroserviceAPIClient(
            zendesk_email=parameters["ZENDESK_EMAIL"],
            zendesk_token=parameters["ZENDESK_TOKEN"],
        )
    else:
        logger.info("Using Halo API")
        api_client = HaloAPIClient(
            halo_subdomain=parameters["HALO_SUBDOMAIN"],
            halo_client_id=parameters["HALO_CLIENT_ID"],
            halo_client_secret=parameters["HALO_CLIENT_SECRET"],
        )
    return api_client


def save_debug_data_to_s3(s3, bucket_name, emails, event, iso_utcnow, parameters, status):
    output_filename = f"lambda-output/incoming-{iso_utcnow}"
    logged_output = {
        "status": status,
        "session_token": aws_session_token,
        "outputFilename": output_filename,
        "datetime": iso_utcnow,
        "emails": [str(email) for email in emails],
        "parameters": parameters,
        "event": event.raw_event,
    }
    if not bucket_name:
        bucket_name = "dbt-help-desk-incoming-mail"
    s3.put_object(
        Bucket=bucket_name,
        Key=output_filename,
        Body=json.dumps(logged_output, indent=4),
    )


def get_email_from_bucket(s3, bucket_name, object_key):
    logger.info(
        "Getting mail from bucket", extra={"bucket_name": bucket_name, "object_key": object_key}
    )
    response = s3.get_object(Bucket=bucket_name, Key=object_key)
    content = response["Body"]
    logger.debug("Got mail from bucket", extra={"mail_content": content})
    return content


def get_iso_utcnow():
    return datetime.utcnow().isoformat()


def get_parameters():
    ssm_client = boto3.client("ssm")
    parameters = {}
    for name in [
        "ZENDESK_EMAIL",
        "ZENDESK_TOKEN",
        "HELP_DESK_API_URL",
        "HALO_SUBDOMAIN",
        "HALO_CLIENT_ID",
        "HALO_CLIENT_SECRET",
    ]:
        parameter = ssm_client.get_parameter(Name=name, WithDecryption=True)
        parameters[name] = parameter["Parameter"]["Value"]  # /PS-IGNORE
    logger.debug("get_parameters", extra={"parameters": parameters})
    return parameters
