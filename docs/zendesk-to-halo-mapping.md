# Defining the mapping from Zendesk custom fields to Halo

## Introduction

Zendesk is configured with a number of custom fields.
In order to convert these to the correct Halo fields, it is necessary to define
a mapping from the Zendesk field ID to the Halo field name.

As it is not possible to automate this mapping process completely,
defining of the mappings is a three stage process:

1. Export the JSON definition of the fields from Zendesk to a CSV file
with the management command `export_zendesk_to_halo_field_mappings`
2. Within a suitable editor (e.g. Numbers or Excel), 
manually add the names of the corresponding Halo custom fields
3. Generate a Python representation of the mappings with the management command
`generate_zendesk_to_halo_field_mappings`

## Management commands

### `export_zendesk_to_halo_field_mappings`

#### Arguments:
| Short name | Long name       | Optional? | Default   | Purpose                                     |
|------------|-----------------|-----------|-----------|---------------------------------------------|
| `-c`       | `--credentials` | No        |           | Email address for Zendesk credentials in DB |
| `-t`       | `--token`       | No        |           | Zendesk API token                           |
| `-p`       | `--prefix`      | Yes       | `uktrade` | Zendesk instance                            |
| `-o`       | `--output`      | Yes       | `stdout`  | Output file path                            |

Use this command to fetch the ticket field definitions from the Zendesk instance
and save them to a CSV file.


### `generate_zendesk_to_halo_field_mappings`

#### Arguments:
| Short name | Long name       | Optional? | Default   | Purpose                              |
|------------|-----------------|-----------|-----------|--------------------------------------|
| `-i`       | `--input`       | No        |           | Zendesk to Halo fields CSV file path |
| `-o`       | `--output`      | Yes       | `stdout`  | Output file path                     |

Use this command to read the CSV file containing the field mappings
and write them to a Python file.

Once satisfied that the generated file is fit for purpose,
it should be placed at `help_desk_api/utils/generated_field_mappings.py`.

