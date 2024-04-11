from typing import Callable

from help_desk_api.utils.utils import (
    action_mappings,
    condition_mappings,
    default_action_description,
    default_condition_description,
)


class ZendeskMacros:
    def __init__(self, macros, zendesk_config=None) -> None:
        self.zendesk_config = zendesk_config if zendesk_config else {}
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

    def document(self):
        context = {
            "type": "macros",
            "instance": self.zendesk_config["instance"],
            "items": [Macro(macro, self.zendesk_config).document() for macro in self.macros],
        }
        return context


class Macro:
    def __init__(self, trigger, zendesk_config):
        self.data = trigger
        self.groups = zendesk_config["groups"] if "groups" in zendesk_config else {}
        self.fields = zendesk_config["fields"] if "fields" in zendesk_config else {}

    def document(self):
        context = {
            "title": self.title,
            "description": self.description,
            # "conditions": {
            #     "all": self.conditions("all"),
            #     "any": self.conditions("any"),
            # },
            "actions": self.actions(),
        }
        return context

    @property
    def title(self):
        return self.data["title"]

    @property
    def description(self):
        description = self.data["description"]
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
