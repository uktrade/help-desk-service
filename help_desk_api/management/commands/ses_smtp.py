from django.core.management import BaseCommand
from email_router.smtp.ses import send_via_ses


class Command(BaseCommand):
    help = "Send an email via SES SMTP"

    def add_arguments(self, parser):
        parser.add_argument(
            "-u",
            "--username",
            type=str,
            help="SMTP username",
            required=True,
        )
        parser.add_argument(
            "-p",
            "--password",
            type=str,
            help="SMTP password",
            required=True,
        )
        parser.add_argument(
            "-t",
            "--to",
            type=str,
            help="To: address",
            required=True,
        )
        parser.add_argument(
            "-s",
            "--subject",
            type=str,
            help="Subject line",
            required=False,
            default="Test of SES SMTP",
        )
        parser.add_argument(
            "-b",
            "--body",
            type=str,
            help="Email body",
            required=False,
            default="""
This is a test of sending email via the SES SMTP endpoint.

If you get this, it worked.

If you keep getting this until your mailbox is full, it worked too much.
            """,
        )

    def handle(self, *args, **options):
        self.stdout.write("Starting send attempt")
        smtp_user = options["username"]
        smtp_password = options["password"]
        message_to = options["to"]
        subject = options["subject"]
        body = options["body"]
        send_via_ses(smtp_user, smtp_password, message_to, subject, body)
        self.stdout.write("Message sent")
