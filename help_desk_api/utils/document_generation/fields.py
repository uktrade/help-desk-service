class ZendeskFields:
    def __init__(self, fields, zendesk_config=None) -> None:
        super().__init__()
        self.zendesk_config = zendesk_config if zendesk_config is not None else {}
        self.fields = fields["ticket_fields"]

    @property
    def custom_fields(self):
        return [field for field in self.fields]  # if "custom_field_options" in field]

    def document(self):
        context = {
            "type": "fields",
            "instance": self.zendesk_config["instance"],
            "items": [
                field  # CustomField(field, self.zendesk_config).document()
                for field in self.custom_fields
            ],
        }
        return context


class CustomField:
    def __init__(self, field, zendesk_config) -> None:
        super().__init__()
        self.field = field

    @property
    def id(self):
        return self.field["id"]

    @property
    def name(self):
        return self.field["title"]

    @property
    def values(self):
        return self.field["custom_field_options"]

    @property
    def has_custom_field_options(self):
        return "Yes" if "custom_field_options" in self.field else "No"

    def document(self):
        return self.field


class HaloField:
    def __init__(self, field):
        super().__init__()
        self.field = field
