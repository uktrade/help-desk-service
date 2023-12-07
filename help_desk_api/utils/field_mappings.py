import inspect
from dataclasses import dataclass

from help_desk_api.utils.utils import fix_csv_boolean


@dataclass
class HaloField:
    halo_id: int
    halo_title: str
    is_zendesk_custom_field: bool


class ZendeskToHaloMapping:
    zendesk_id: int = 0
    zendesk_title: str = ""
    is_zendesk_custom_field: bool = False
    halo_id: int = 0
    halo_title: str = ""
    special_treatment: bool = False

    def __init__(self, **kwargs):
        super().__init__()
        for name, value in kwargs.items():
            attr = getattr(self, name, None)
            if attr is not None:
                try:
                    attr_type = type(attr)
                    if attr_type is bool:
                        value = fix_csv_boolean(value)
                    else:
                        value = attr_type(value)
                except TypeError:
                    value = None
                except ValueError:
                    value = None
            setattr(self, name, value)

    def __repr__(self):
        constructor_kwargs = []
        for member in inspect.getmembers(self):
            if not member[0].startswith("__"):
                if not inspect.ismethod(member[1]):
                    constructor_kwargs.append(f"{member[0]}={repr(member[1])}")

        return f"{self.__class__.__name__}({', '.join(constructor_kwargs)})"
