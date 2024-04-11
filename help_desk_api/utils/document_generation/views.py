from typing import Callable

from help_desk_api.utils.utils import (
    action_mappings,
    condition_mappings,
    default_action_description,
    default_condition_description,
    group_id_to_name,
)


class ZendeskViews:
    def __init__(self, views, zendesk_config=None) -> None:
        self.zendesk_config = zendesk_config if zendesk_config else {}
        super().__init__()
        self.views = [view for view in views["views"] if view["active"]]

    def document(self):
        context = {
            "type": "views",
            "instance": self.zendesk_config["instance"],
            "items": [View(view, self.zendesk_config).document() for view in self.views],
        }
        return context


class View:
    def __init__(self, view, zendesk_config):
        self.data = view
        self.groups = zendesk_config["groups"] if "groups" in zendesk_config else {}
        self.fields = zendesk_config["fields"] if "fields" in zendesk_config else {}

    def document(self):
        context = {
            "title": self.title,
            "description": self.description,
            "restriction": self.restriction,
            "conditions": {
                "all": self.conditions("all"),
                "any": self.conditions("any"),
            },
            "execution": self.execution,
            # "actions": self.actions(),
        }
        return context

    @property
    def execution(self):
        execution = self.data["execution"]
        output = {
            "columns": [column["title"] for column in execution["columns"]],
        }
        if not execution["sort"]:
            output["sorting"] = "n/a"
        else:
            output["sorting"] = f"{execution['sort']['title']} {execution['sort']['order']}"
        if not execution["group"]:
            output["grouping"] = "n/a"
        else:
            output["grouping"] = f"{execution['group']['title']} {execution['group']['order']}"
        return output

    @property
    def title(self):
        return self.data["title"]

    @property
    def description(self):
        description = self.data["description"]
        if description is None:
            description = "No description given"
        return description

    @property
    def restriction(self):
        restriction = self.data["restriction"]
        if restriction is None:
            return ["All agents"]
        if restriction["type"] == "Group":
            return [group_id_to_name(self.groups, str(group_id)) for group_id in restriction["ids"]]
        elif restriction["type"] == "User":
            ids = restriction.get("ids", [restriction["id"]])
            return ids

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
