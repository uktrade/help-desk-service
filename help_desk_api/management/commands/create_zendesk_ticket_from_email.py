import json
import os
import pathlib
from datetime import datetime
from email.utils import parseaddr

from django.conf import settings
from django.core.management import BaseCommand
from email_router.ses_email_receiving.email_utils import ParsedEmail
from zenpy import Zenpy
from zenpy.lib.api_objects import Comment, CustomField, Ticket, User


class Command(BaseCommand):
    help = "Create ticket on Zendesk by the same mechanism as email"  # /PS-IGNORE

    def __init__(self, stdout=None, stderr=None, **kwargs):
        super().__init__(stdout, stderr, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            "-c",
            "--credentials",
            type=str,
            help="Email address linked to Halo credentials",
            required=True,
        )
        parser.add_argument(
            "-t",
            "--token",
            type=str,
            help="Zendesk API token",
            required=True,
        )
        parser.add_argument(
            "-u",
            "--microservice",
            type=bool,
            help="Zendesk API token",
            default=False,
        )
        parser.add_argument(
            "-e", "--email", type=pathlib.Path, help="Email file path", required=True
        )
        parser.add_argument(
            "-o", "--output", type=pathlib.Path, help="Output file path (default: stdout)"
        )

    def handle(self, *args, **options):
        parsed_email = None
        with open(options["email"], "rb") as email_file:
            parsed_email = ParsedEmail(raw_bytes=email_file)

        if options["microservice"]:
            os.environ["ZENPY_FORCE_NETLOC"] = "help-desk-service-staging.london.cloudapps.digital"

        client = Zenpy(
            subdomain="staging-uktrade", email=options["credentials"], token=options["token"]
        )

        timestamp = datetime.utcnow().isoformat()
        via = "via μservice" if options["microservice"] else "directly"
        subject = f"{parsed_email.subject} (Posted {via} at {timestamp})"
        description = parsed_email.payload
        recipient = parseaddr(parsed_email.recipient)[1]

        upload_tokens = []
        for attachment in parsed_email.attachments:
            payload = attachment["payload"]
            filename = attachment["filename"]
            content_type = attachment["content_type"]
            upload = client.attachments.upload(
                payload, target_name=filename, content_type=content_type
            )
            upload_tokens.append(upload.token)

        zenpy_user = User(
            email=parsed_email.sender_email,
            name=f"test-{datetime.utcnow().microsecond} {parsed_email.sender_name}",
        )
        zenpy_ticket = Ticket(
            subject=subject,
            comment=Comment(
                html_body=description,
                uploads=upload_tokens,
            ),
            requester=zenpy_user,
            custom_fields=[CustomField(id=31281329, value="datahub")],
            recipient=recipient,
        )

        ticket_audit = client.tickets.create(zenpy_ticket)

        # ticket_audit.ticket.comment = Comment(body="private_comment", public=False)
        # client.tickets.update(ticket_audit.ticket)

        ticket = ticket_audit.ticket
        ticket_id = ticket.id

        output = {"ticket_id": ticket_id}

        if options["output"]:
            output_path = options["output"].with_name(
                options["output"].name.format(ticketid=ticket_id, timestamp=timestamp)
            )
            output_path = settings.BASE_DIR / output_path
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as output_file:
                json.dump(output, output_file, indent=4)
                print(f"Output written to {output_path}")
        else:
            json.dump(output, self.stdout, indent=4)
