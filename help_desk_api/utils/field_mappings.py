import inspect
from dataclasses import dataclass


class StringInt:
    def __init__(self, *, default=0):
        self._default = default

    def __set_name__(self, owner, name):
        self._name = "_" + name

    def __get__(self, obj, type):
        if obj is None:
            return self._default
        return getattr(obj, self._name, self._default)

    def __set__(self, obj, value):
        setattr(obj, self._name, int(value))


class StringBool:
    def __init__(self, *, default="FALSE"):
        self._default = default

    def __set_name__(self, owner, name):
        self._name = "_" + name

    def __get__(self, obj, type):
        if obj is None:
            return self._default
        return getattr(obj, self._name, self._default)

    def __set__(self, obj, value):
        setattr(obj, self._name, value in ["TRUE", "True", "1", 1, True])


@dataclass
class HaloField:
    halo_id: int
    halo_title: str
    is_zendesk_custom_field: bool


@dataclass
class ZendeskToHaloMapping:
    zendesk_id: StringInt = StringInt()
    zendesk_title: str = ""
    is_zendesk_custom_field: StringBool = StringBool()
    halo_id: int = 0
    halo_title: str = ""
    special_treatment: StringBool = StringBool()
    value_mappings: dict | None = None

    def __repr__(self):
        constructor_kwargs = []
        for member in inspect.getmembers(self):
            if not member[0].startswith("_"):
                if not inspect.ismethod(member[1]):
                    constructor_kwargs.append(f"{member[0]}={repr(member[1])}")

        return f"{self.__class__.__name__}({', '.join(constructor_kwargs)})"
