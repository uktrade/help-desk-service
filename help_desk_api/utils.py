import base64
import re

from rest_framework import authentication, exceptions


def get_zenpy_request_vars(request):
    encoded_auth = authentication.get_authorization_header(request)
    if not encoded_auth:
        raise exceptions.NotAuthenticated("No Authorization header found")
    auth_parts = encoded_auth.decode("utf-8").split(" ")

    auth_header = base64.b64decode(auth_parts[1])  # /PS-IGNORE
    creds_parts = auth_header.decode("utf-8").split(":")

    email = creds_parts[0].replace("/token", "")

    try:
        token = creds_parts[1]
    except UnicodeError:
        msg = "Invalid token header. Token string should not contain invalid characters."
        raise exceptions.AuthenticationFailed(msg)

    return token, email


class ZenpyMacros:
    def __init__(self, macros) -> None:
        super().__init__()
        self._macros = macros["macros"]

    @property
    def macros(self):
        return self._macros

    @property
    def unique_actions(self):
        actions = [action["field"] for macro in self.macros for action in macro["actions"]]
        return sorted(list(set(actions)))

    @property
    def plaintext_comments(self):
        comments = [
            action["value"]
            for macro in self.macros
            for action in macro["actions"]
            if isinstance(action["value"], str) and action["field"] == "comment_value"
        ]
        comments += [
            action["value"][1]
            for macro in self.macros
            for action in macro["actions"]
            if isinstance(action["value"], list) and action["field"] == "comment_value"
        ]
        return sorted(list(set(comments)))

    @property
    def html_comments(self):
        comments = [
            action["value"]
            for macro in self.macros
            for action in macro["actions"]
            if isinstance(action["value"], str) and action["field"] == "comment_value_html"
        ]
        comments += [
            action["value"][1]
            for macro in self.macros
            for action in macro["actions"]
            if isinstance(action["value"], list) and action["field"] == "comment_value_html"
        ]
        return sorted(list(set(comments)))

    @property
    def subjects(self):
        comments = [
            action["value"]
            for macro in self.macros
            for action in macro["actions"]
            if action["field"] == "subject"
        ]
        return sorted(list(set(comments)))


class ZenpyTriggers:
    def __init__(self, triggers) -> None:
        super().__init__()
        self._triggers = triggers["triggers"]

    def filter_function(self, item):
        if "actions" not in item:
            return False
        for action in item["actions"]:
            if action["field"] == "notification_user":
                return True
        return False

    @property
    def triggers(self):
        if self._triggers is None:
            self._triggers = []
        return self._triggers

    def email_action_only(self, trigger):
        email_actions = [
            action for action in trigger["actions"] if action["field"] == "notification_user"
        ]
        reduced_trigger = {"title": trigger["title"], "email_actions": email_actions}
        return reduced_trigger

    @property
    def email_actions(self):
        triggers_with_email_actions = [
            self.email_action_only(trigger)
            for trigger in self.triggers
            if self.filter_function(trigger)
        ]

        return triggers_with_email_actions

    @property
    def unique_emails(self):
        """
        Some triggers send identical emails to several people.
        No sense in having multiple versions of the email template.
        """
        emails = []
        distinct_emails = set()
        for action in self.email_actions:
            for index, email_action in enumerate(action["email_actions"]):
                subject = email_action["value"][1]
                body = email_action["value"][2]
                subject_and_body = f"<subject: {subject}><body: {body}>"
                if subject_and_body in distinct_emails:
                    continue
                distinct_emails.add(subject_and_body)
                emails.append(
                    {
                        "title": f"{action['title']}",
                        "subject": subject,
                        "body": body,
                    }
                )
        return emails


class PlaceholderMapper:
    _mappings = {
        "#{{ticket.id}}": "[$FAULTID]($LINKTOREQUESTUSER)",
        "{{ticket.id}}": "$FAULTID",  # /PS-IGNORE
        "{{ticket.requester.email}}": "$USEREMAILADDRESS",
        "{{ticket.requester.first_name}}": "$FIRSTNAME",  # /PS-IGNORE
        "{{ticket.title}}": "$SYMPTOM",  # /PS-IGNORE
        "{{ticket.description}}": "$SYMPTOM2",
        "{{ticket.group.name}}": "$SECTION",
        "{{ticket.link}}": "$LINKTOREQUESTUSER",
        "{{ticket.status}}": "$STATUS",
        "{{ticket.requester.name}}": "$USERNAME",
        "{{ticket.assignee.name}}": "$ASSIGNEDTO",  # /PS-IGNORE
    }
    _mapping_re = None

    @property
    def mapping_re(self):
        if self._mapping_re is None:
            self._mapping_re = re.compile("|".join(self._mappings.keys()))
        return self._mapping_re

    def map(self, text):
        return self.mapping_re.sub(lambda match: self._mappings[match.group()], text)
