import base64
import re

from rest_framework import authentication, exceptions


def apply_zendesk_automatic_html(text: str):
    """
    Zendesk automatically converts certain things to HTML.
    Halo doesn't.
    So we apply what we can to try to make things a bit consistent.
    """
    text_with_links = create_links(text)
    text_with_html_breaks = create_html_breaks(text_with_links)
    return text_with_html_breaks


def create_links(text):
    """
    TODO: convert URLs and email addresses
    """
    return text


def create_html_breaks(text):
    """
    Markdown ignores a single \n
    whereas Zendesk add <br> for them in descriptions
    """
    modified_text = re.sub(r"(?<!\n)\n(?!\n)", "<br>\n", text)
    return modified_text


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


# Operators

operator_mappings = {
    "is": "is",
    "is_not": "is NOT",
    "value": "value changed to",
    "not_value": "value NOT changed to",
    "value_previous": "value changed from",
    "not_value_previous": "NOT changed from",
    "not_changed": "NOT changed",
}


def operator(value):
    return operator_mappings.get(value, value)


# Utility functions


def group_id_to_name(groups, group_id):
    if group_id == "current_groups":
        return group_id
    return groups.get(group_id, "Unknown group")


def custom_field_id_to_name(fields, field):
    custom_field_id = field.replace("custom_fields_", "")
    return fields[custom_field_id]


# Conditions


def email_to(condition, *args, **kwargs):
    return {
        "label": "Received at email address",
        "value": condition["value"],
        "type": condition["field"],
        "help": "The email address at which the ticket was received",
    }


def status(condition, *args, **kwargs):
    return {
        "label": f"Ticket status {operator(condition['operator'])}",
        "value": condition["value"],
        "type": condition["field"],
        "help": """
        The state of the ticket.
        Allowed values are "new", "open", "pending", "hold", "solved", or "closed".
        """,
    }


def group_condition(condition, *args, groups=None, **kwargs):
    return {
        "label": "Group (aka Team)",
        "value": group_id_to_name(groups, condition["value"]),
        "type": condition["field"],
        "help": "The group assigned to the ticket.",
    }


def custom_field_condition(condition, *args, fields=None, **kwargs):
    return {
        "label": custom_field_id_to_name(fields, condition["field"]),
        "value": condition["value"],
        "type": condition["field"],
        "help": "Specify the custom  field.",
    }


def update_type_condition(condition, *args, **kwargs):
    return {
        "label": "Ticket update type",
        "value": condition["value"],
        "type": condition["field"],
        "help": """
        "Create" - trigger will be applied if the ticket has just been created.
        "Change" - trigger will be applied if the ticket already existed but has changed.
        """,
    }


def comment_includes_word_condition(condition, *args, **kwargs):
    operator = condition["operator"]
    if operator == "is_not":
        effect = "does not equal the string"
    elif operator == "is":
        effect = "equals the string"
    elif operator == "includes":
        effect = "includes the string"
    elif operator == "not_includes":
        effect = "does not include the string"
    else:
        effect = f"<span class='todo'>{condition['field']} with unknown operator</span>"
    return {
        "label": f"Comment {effect}",
        "value": condition["value"],
        "type": condition["field"],
        "help": "Single words or strings in either the subject or body of the comment.",
    }


def subject_includes_word_condition(condition, *args, **kwargs):
    return_value = comment_includes_word_condition(condition, *args, **kwargs)
    return_value["help"] = "Single words or strings in the subject of the comment only."
    return return_value


def requester_id_condition(condition, *args, **kwargs):
    return {
        "label": "Requester ID",
        "value": condition["value"],
        "type": condition["field"],
        "help": """
        "" (no requester specified), "current_user", or the numeric id of the requester or assignee
        """,
    }


def assignee_id_condition(condition, *args, **kwargs):
    return {
        "label": "Assignee ID",
        "value": condition["value"],
        "type": condition["field"],
        "help": """
        "" (nobody assigned to the ticket), "current_user",
        or the numeric id of the agent assigned to the ticket
        """,
    }


def current_tags_condition(condition, *args, **kwargs):
    return {
        "label": "Current tags",
        "value": condition["value"],
        "type": condition["field"],
        "help": """
        A space-delimited list of tags to compare against the ticket's tags.
        """,
    }


def comment_is_public_condition(condition, *args, **kwargs):
    return {
        "label": "Current tags",
        "value": condition["value"],
        "type": condition["field"],
        "help": """
        true, false, "not_relevant" (present), or "
        requester_can_see_comment" (present and requester can see comment)
        """,
    }


def via_id_condition(condition, *args, **kwargs):
    via_channels = {"4": "email"}
    channel = via_channels.get(condition["value"], condition["value"])
    return {
        "label": "Ticket came via channel",
        "value": f"{channel} (via_id: {condition['value']})",
        "type": condition["field"],
        "help": """
        The numeric id of the channel used to create the ticket.
        """,
    }


def organization_id_condition(condition=None, **kwargs):
    return {
        "label": "Organization ID",
        "value": f"{condition['value']} - Bespoke Solutions Dotnet",
        "type": condition["field"],
        "help": """
        "" (no organization added to the ticket)
        or the numeric id of the organization added to the ticket
        """,
    }


def type_condition(condition=None, **kwargs):
    return {
        "label": "Type",
        "value": condition["value"],
        "type": condition["field"],
        "help": """
        "question", "incident", "problem", or "task"
        """,
    }


def description_includes_word_condition(condition=None, **kwargs):
    return {
        "label": "Description includes word(s)",
        "value": condition["value"],
        "type": condition["field"],
        "help": """
        Single words or strings in the ticket subject.
        Operator can be:<br>
        "includes" (contains one word),
        "not_includes" (contains none of the words),
        "is" (contains string),
        "is_not" (does not contain string)
        """,
    }


def satisfaction_score_condition(condition=None, **kwargs):
    return {
        "label": "Satisfaction Score",
        "value": condition["value"],
        "type": condition["field"],
        "help": """
        Possible values: "good_with_comment", "good", "bad_with_comment",
        "bad", false (offered), or true (unoffered).
        Operator can be:<br>
        "includes" (contains one word),
        "not_includes" (contains none of the words),
        "is" (contains string),
        "is_not" (does not contain string)
        """,
    }


def due_at_condition(condition=None, **kwargs):
    return {
        "label": "Due At",
        "value": condition["value"],
        "type": condition["field"],
        "help": """
        <span class="highlight>This presumably relates to the due date for the ticket,
        but this condition is not mentioned in the Zendesk documentation.</span>
        """,
    }


def updated_at_condition(condition=None, **kwargs):
    return {
        "label": "Updated At",
        "value": condition["value"],
        "type": condition["field"],
        "help": """
        Hours since update.
        """,
    }


def priority_condition(condition=None, **kwargs):
    return {
        "label": "Priority",
        "value": condition["value"],
        "type": condition["field"],
        "help": """
        "" (no priority assigned to the ticket),
        "low", "normal", "high", or "urgent".
        """,
    }


def new_condition(condition=None, **kwargs):
    return {
        "label": "NEW",
        "value": condition["value"],
        "type": condition["field"],
        "help": """
        Hours since the ticket was created.
        """,
    }


def solved_condition(condition=None, **kwargs):
    return {
        "label": "SOLVED",
        "value": condition["value"],
        "type": condition["field"],
        "help": """
        Hours since the ticket was changed to solved.
        """,
    }


condition_mappings = {
    "recipient": email_to,
    "status": status,
    "group_id": group_condition,
    "custom_field": custom_field_condition,
    "update_type": update_type_condition,
    "comment_includes_word": comment_includes_word_condition,
    "subject_includes_word": subject_includes_word_condition,
    "requester_id": requester_id_condition,
    "assignee_id": assignee_id_condition,
    "current_tags": current_tags_condition,
    "comment_is_public": comment_is_public_condition,
    "via_id": via_id_condition,
    "organization_id": organization_id_condition,
    "type": type_condition,
    "description_includes_word": description_includes_word_condition,
    "satisfaction_score": satisfaction_score_condition,
    "due_at": due_at_condition,
    "updated_at": updated_at_condition,
    "priority": priority_condition,
    "NEW": new_condition,
    "SOLVED": solved_condition,
}


def default_condition_description(*args, **kwargs):
    condition = kwargs.get("condition")
    return {
        "label": f"<span class='todo'>{condition['field']}</span>",
        "value": condition["value"],
        "type": condition["field"],
        "help": None,
    }


# Actions


def action_group_id_to_name(action=None, groups=None, **kwargs):
    group_name = group_id_to_name(groups, action["value"])
    return {
        "label": "Set Group (aka Team)",
        "value": group_name,
        "raw_action": action["field"],
        "help": """
        Assigns the ticket to a group. Takes a string with a group id, or an empty string ("")
        to unassign the group assigned to the ticket.
        """,
    }


def action_custom_field_id_to_name(action=None, fields=None, **kwargs):
    field_name = custom_field_id_to_name(fields, action["field"])
    return {
        "label": f"Set custom field <strong>{field_name}</strong>",
        "value": action["value"],
        "raw_action": action["field"],
        "help": """
        Sets the value of a custom ticket field.
        """,
    }


def group_notification_action(action=None, groups=None, **kwargs):
    group_name = group_id_to_name(groups, action["value"][0])
    return {
        "label": f"Notify group <strong>{group_name}</strong>",
        "value": action["value"],
        "raw_action": action["field"],
        "help": """
        Sends an email to a group.
        Takes an array of three strings specifying the email recipient, subject, and body.
        Possible recipient value: "group_id" (the currently assigned group),
        or the numeric ID of a group
        """,
    }


def set_tags_action(action=None, **kwargs):
    return {
        "label": "Replace tags",
        "value": action["value"],
        "raw_action": action["field"],
        "help": """
        A space-delimited list of tags to insert in the ticket.
        <strong>The action replaces the current tags.</strong>
        """,
    }


def remove_tags_action(action=None, **kwargs):
    return {
        "label": "Remove tags",
        "value": action["value"],
        "raw_action": action["field"],
        "help": """
        A space-delimited list of tags to remove from existing tags.
        """,
    }


def current_tags_action(action=None, **kwargs):
    return {
        "label": "Add to tags",
        "value": action["value"],
        "raw_action": action["field"],
        "help": """
        A space-delimited list of tags to add to existing tags.
        """,
    }


def notification_webhook_action(action=None, **kwargs):
    return {
        "label": "Notification sent to WebHook",
        "value": "Tokens and stuff - can deal with this separately.",
        "raw_action": action["field"],
        "help": """
        Sends a message to an active webhook.
        Takes an array of two strings specifying the unique ID
        of the webhook and the message body.
        """,
    }


def notification_target_action(action=None, **kwargs):
    return {
        "label": "Notification sent to Target",
        "value": """
        Tokens and stuff - can deal with this separately<br>
        N.B. No targets are configured, so this seems to be a NOOP.
        """,
        "raw_action": action["field"],
        "help": """
        Sends a message to an external target.
        Takes an array of two strings specifying the numeric ID of the target and the message body.
        """,
    }


def priority_action(action=None, **kwargs):
    return {
        "label": "Ticket Priority",
        "value": action["value"],
        "raw_action": action["field"],
        "help": """
        Sets the ticket priority. Takes "low", "normal", "high", or "urgent".
        """,
    }


def status_action(action=None, **kwargs):
    return {
        "label": "Ticket Status",
        "value": action["value"],
        "raw_action": action["field"],
        "help": """
        Sets the ticket status. Takes "new", "open", "pending", "hold", "solved", or "closed".
        """,
    }


def comment_value_html_action(action=None, **kwargs):
    return {
        "label": "Add Comment - HTML",
        "value": action["value"],
        "raw_action": action["field"],
        "help": """
        Adds a rich-text comment to a ticket.
        """,
    }


def assignee_id_action(action=None, **kwargs):
    return {
        "label": "Assign Ticket",
        "value": action["value"],
        "raw_action": action["field"],
        "help": """
        Assigns the ticket to a person.
        Takes a string with the user id of an assignee or requester,
        or "current_user",
        or an empty string ("") to unassign the person assigned to the ticket.
        """,
    }


def type_action(action=None, **kwargs):
    return {
        "label": "Type",
        "value": action["value"],
        "raw_action": action["field"],
        "help": """
        Sets the ticket type. Takes "question", "incident", "problem", or "task".
        """,
    }


def comment_mode_is_public_action(action=None, **kwargs):
    return {
        "label": "Make comment public or private",
        "value": action["value"],
        "raw_action": action["field"],
        "help": """
        Makes a ticket comment public or private.
        Takes true (public) or false (private).
        """,
    }


def subject_action(action=None, **kwargs):
    return {
        "label": "Subject",
        "value": action["value"],
        "raw_action": action["field"],
        "help": """
        Replaces the subject of a ticket. Takes the subject text.
        """,
    }


def comment_value_action(action=None, **kwargs):
    return {
        "label": "Add Comment - Plain text",
        "value": action["value"],
        "raw_action": action["field"],
        "help": """
        Adds a comment to a ticket.
        Takes the comment text or an array of two strings
        specifying the comment channel and comment text.
        Possible comment channels : "channel:all", "channel:web" and "channel:chat".
        """,
    }


def cc_action(action=None, **kwargs):
    return {
        "label": "CC",
        "value": action["value"],
        "raw_action": action["field"],
        "help": """
        CC's somebody on the ticket. Takes "current_user" or the numeric ID of an agent.
        """,
    }


def ticket_form_id_action(action=None, **kwargs):
    return {
        "label": "Ticket form ID",
        "value": action["value"],
        "raw_action": action["field"],
        "help": """
        Enterprise only. The id of the ticket form to render for the ticket.
        <strong style="color: red;">
        This is only used once in this macro that includes "TEST" in its title,
        so can almost certainly be ignored.
        </strong>
        """,
    }


def notification_user_action(action=None, groups=None, **kwargs):
    to, subject, body = action["value"]
    if to in groups:
        to = group_id_to_name(groups, to)
    if to not in ["current_user", "all_agents", "requester_id", "assignee_id"]:
        to = "Not a group, user, all agents, or assignee: probably a specific agent"
    return {
        "label": "Email User",
        "value": f"""
        To: {to}<br>
        Subject: {subject}<br>
        Body: {body}
        """,
        "raw_action": action["field"],
        "help": """
        Sends an email to a user.
        Takes an array of three strings specifying the email recipient, subject, and body.
        Possible recipient value:
        <ul>
        <li><code>"current_user"</code>
        <li><code>"all_agents"</code> (all non-restricted agents)
        <li><code>"requester_id"</code> (the current requester)
        <li><code>"assignee_id"</code> (the current assignee)
        <li>or the numeric ID of an agent.</ul>
        """,
    }


def satisfaction_score_action(action=None, **kwargs):
    return {
        "label": "Send Satisfaction Survey",
        "value": action["value"],
        "raw_action": action["field"],
        "help": """
        Sends a survey request to the ticket requester. Takes "offered" as a value.
        """,
    }


def default_action_description(*args, **kwargs):
    action = kwargs.get("action")
    return {
        "label": "<span class='todo'>TODO</span>",
        "value": action["value"],
        "raw_action": action["field"],
        "help": """
        <span class='todo'>FIX NEEDED</span>
        """,
    }


action_mappings = {
    "group_id": action_group_id_to_name,
    "custom_field": action_custom_field_id_to_name,
    "notification_group": group_notification_action,
    "set_tags": set_tags_action,
    "current_tags": current_tags_action,
    "remove_tags": remove_tags_action,
    "notification_webhook": notification_webhook_action,
    "notification_target": notification_target_action,
    "priority": priority_action,
    "status": status_action,
    "assignee_id": assignee_id_action,
    "notification_user": notification_user_action,
    "comment_value_html": comment_value_html_action,
    "type": type_action,
    "comment_mode_is_public": comment_mode_is_public_action,
    "subject": subject_action,
    "comment_value": comment_value_action,
    "cc": cc_action,
    "ticket_form_id": ticket_form_id_action,
    "satisfaction_score": satisfaction_score_action,
}
