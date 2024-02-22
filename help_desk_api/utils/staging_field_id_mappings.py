"""
Some services such as Data Workspace are configured with
custom field IDs and values corresponding to the staging
Zendesk instance. So they need to be mapped to the expected
values for Halo.
"""
from collections import namedtuple

SpecialCase = namedtuple("SpecialCase", ["replacement_id", "replacement_value"])

special_cases = {"44394845": SpecialCase("31281329", "data_workspace")}
