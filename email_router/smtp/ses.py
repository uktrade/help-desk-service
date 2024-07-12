import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def send_via_ses(user, password, to_address, subject="Test SMTP", body="This be the email"):
    port = 587  # For SSL  /PS-IGNORE
    smtp_server = os.environ.get("TEST_SMTP_SERVER")  # /PS-IGNORE
    from_address = os.environ.get("TEST_SMTP_FROM_ADDRESS")

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = from_address
    message["To"] = to_address
    text = body
    message.attach(MIMEText(text, "plain"))

    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls()
        server.login(user, password)
        server.sendmail(from_address, to_address, message.as_string())
