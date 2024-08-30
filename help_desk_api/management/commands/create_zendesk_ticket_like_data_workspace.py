import json
import os
import pathlib
from datetime import datetime

from django.conf import settings
from django.core.management import BaseCommand
from zenpy import Zenpy
from zenpy.lib.api_objects import Comment, CustomField, Ticket, User


class Command(BaseCommand):
    help = "Create ticket on Zendesk by the same mechanism as Data Workspace"  # /PS-IGNORE

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
            "-o", "--output", type=pathlib.Path, help="Output file path (default: stdout)"
        )

    def handle(self, *args, **options):

        if options["microservice"]:
            # url = "https://help-desk-service-staging.london.cloudapps.digital/api/v2/tickets.json"
            os.environ["ZENPY_FORCE_NETLOC"] = "internal.staging.help-desk-service.uktrade.digital"
        else:
            #     url = f"https://staging-uktrade.zendesk.com/api/v2/tickets.json"
            # url = f"http://localhost:8000/api/v2/tickets.json"
            pass

        client = Zenpy(
            subdomain="staging-uktrade", email=options["credentials"], token=options["token"]
        )

        timestamp = datetime.utcnow().isoformat()
        via = "via μservice" if options["microservice"] else "directly"
        subject = f"Access Request Posted {via} on DBT Platform at {timestamp}"
        description = f"""Access request for

Username:   username
Journey:    Tool access
Dataset:    catalogue_item
SSO Login:  access_request.requester.email
People search: people_url


Details for the request can be found at

access_request_url

Posted {via} at {timestamp}
        """

        ticket_audit = client.tickets.create(
            Ticket(
                subject=subject,
                description=description,
                requester=User(
                    email="test@example.com",  # /PS-IGNORE
                    name="Test Name1487665",
                ),
                custom_fields=[CustomField(id=31281329, value="data_workspace")],
            )
        )

        ticket_audit.ticket.comment = Comment(
            body="Private_comment containing various supplementary details of the requester",
            public=False,
        )
        client.tickets.update(ticket_audit.ticket)

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
