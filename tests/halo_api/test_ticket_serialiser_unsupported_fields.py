import pytest

from help_desk_api.serializers import (
    HaloDetailsFromZendeskField,
    HaloSummaryFromZendeskField,
    HaloTagsFromZendeskField,
)


class TestTicketSerialisersUnsupportedFields:
    """
    Unsupported fields in Zendesk API data are found
    by removing the original field from the data when
    the field is consumed by the serialiser.
    Thus, if any fields are left after serialisation,
    they must be unsupported. QED.  /PS-IGNORE
    """

    @pytest.mark.parametrize(
        "field_class, input_data, input_field_name",
        [
            (HaloSummaryFromZendeskField, {"subject": ""}, "subject"),
            (HaloDetailsFromZendeskField, {"comment": {"body": ""}}, "comment"),
            (HaloDetailsFromZendeskField, {"description": ""}, "description"),
            (
                HaloTagsFromZendeskField,
                {
                    "tags": [
                        "a",
                        "b",
                        "c",
                    ]
                },
                "tags",
            ),
        ],
    )
    def test_serializer_fields_remove_zendesk_values(
        self, field_class, input_data, input_field_name
    ):
        serialiser_field = field_class()
        serialiser_field.get_attribute(input_data)

        assert input_field_name not in input_data

    # def test_custom_field_serializer_removes_zendesk_values(self):
    #     input_data = {
    #         "custom_fields": [
    #             {"id": 123, "value": "abc"}
    #         ]
    #     }
    #     serializer = HaloCustomFieldsSerializer(source="custom_fields")  /PS-IGNORE
    #     serializer.to_representation(input_data)
    #
    #     assert "custom_fields" not in input_data
