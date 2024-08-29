# Defining the mapping from Zendesk custom fields to Halo

Zendesk is configured with a number of custom fields.
In order to map these to Halo fields, it is necessary to define
a mapping from the Zendesk field ID to the Halo field ID.

In addition, many of these fields (particularly in `dit.zendesk.com`) are multiselect, with textual values.
Such values also need to be mapped to the equivalent Halo ID.

This mapping is achieved using two model classes:
* `help_desk_api.models.CustomField`
* `help_desk_api.models.Value`

All the existing fields have had the appropriate mappings generated.
These are contained in `help_desk_api/initial_data/custom_field_data.json`
and are applied on deployment by the data migration
`help_desk_api/migrations/0009_load_initial_custom_field_data.py`.

Adding new fields or making modifications to existing fields can be carried out in the Django Admin.
