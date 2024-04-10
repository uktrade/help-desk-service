from typing import Callable

from help_desk_api.utils.utils import (
    action_mappings,
    condition_mappings,
    default_action_description,
    default_condition_description,
)


class ZendeskTriggers:
    def __init__(self, triggers, zendesk_config=None) -> None:
        self.zendesk_config = zendesk_config if zendesk_config else {}
        super().__init__()
        self._triggers = triggers["triggers"]

    @property
    def active_triggers(self):
        return [trigger for trigger in self.triggers if trigger["active"]]

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

    def document(self):
        context = {
            "type": "triggers",
            "instance": self.zendesk_config["instance"],
            "items": [
                Trigger(trigger, self.zendesk_config).document() for trigger in self.active_triggers
            ],
        }
        return context


class Trigger:
    def __init__(self, trigger, zendesk_config):
        self.data = trigger
        self.groups = zendesk_config["groups"] if "groups" in zendesk_config else {}
        self.fields = zendesk_config["fields"] if "fields" in zendesk_config else {}

    def document(self):
        context = {
            "title": self.title,
            "description": self.description,
            "conditions": {
                "all": self.conditions("all"),
                "any": self.conditions("any"),
            },
            "actions": self.actions(),
        }
        return context

    @property
    def title(self):
        return self.data["title"]

    @property
    def description(self):
        description = self.data.get("description", None)
        if description is None:
            description = "No description given"
        return description

    def conditions(self, quantifier="all"):
        if not self.data["conditions"][quantifier]:
            return []
        output = []
        for condition in self.data["conditions"][quantifier]:
            output.append(self.condition_to_description(condition))
        return output

    def condition_to_description(self, condition):
        field: str = condition["field"]
        if field.startswith("custom_fields_"):
            processor: Callable = condition_mappings.get(
                "custom_field", default_condition_description
            )
        else:
            processor: Callable = condition_mappings.get(
                condition["field"], default_condition_description
            )
        value = processor(condition=condition, groups=self.groups, fields=self.fields)
        value["operator"] = condition["operator"]
        return value

    def actions(self):
        output = []
        for action in self.data["actions"]:
            output.append(self.action_to_description(action))
        return output

    def action_to_description(self, action):
        field: str = action["field"]
        if field.startswith("custom_fields_"):
            processor: Callable = action_mappings.get("custom_field", default_action_description)
        else:
            processor: Callable = action_mappings.get(action["field"], default_action_description)
        value = processor(action=action, groups=self.groups, fields=self.fields)
        return value


class ZendeskAutomations(ZendeskTriggers):
    def __init__(self, automations, zendesk_config=None) -> None:
        try:
            super().__init__(automations, zendesk_config)
        except KeyError:
            self.automations = automations["automations"]

    def document(self):
        context = {
            "type": "automations",
            "instance": self.zendesk_config["instance"],
            "items": [
                Automation(automation, self.zendesk_config).document()
                for automation in self.automations
            ],
        }
        return context


class Automation(Trigger):
    def document(self):
        context = {
            "title": self.title,
            "conditions": {
                "all": self.conditions("all"),
                "any": self.conditions("any"),
            },
            "actions": self.actions(),
        }
        return context
