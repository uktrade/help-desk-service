from help_desk_api.serializers import HaloCustomFieldsSerializer


class TestExportSupportServiceTicket:
    def test_emergency_form_dummy_values_are_ignored(self, ess_emergency_form_dummy_custom_fields):
        """
        The Ukraine/Russia and Israel/Palestine forms were made in a rush. /PS-IGNORE
        As a result, they deal with some required fields that aren't required
        in their case by sending a "-" dash.
        This obviously falls over when serialised for Halo,
        so those values needs to be discarded.
        """
        serialiser = HaloCustomFieldsSerializer()
        halo_equivalent = serialiser.to_representation(ess_emergency_form_dummy_custom_fields)

        assert not halo_equivalent

    def test_emergency_form_serialises(
        self, ess_russia_ukraine_enquiry, ess_emergency_form_dummy_custom_fields
    ):
        serialiser = HaloCustomFieldsSerializer()

        halo_equivalent = serialiser.to_representation(
            ess_russia_ukraine_enquiry["ticket"]["custom_fields"]
        )

        assert None not in halo_equivalent

    def test_ess_business_type_finds_correct_mapping(self, ess_ticket_request_json):
        serialiser = HaloCustomFieldsSerializer()

        halo_equivalent = serialiser.to_representation(
            ess_ticket_request_json["ticket"]["custom_fields"]
        )

        business_type_fields = list(
            filter(
                lambda field: "name" in field and field["name"] == "CFESSBusinessType",
                halo_equivalent,
            )
        )

        assert business_type_fields is not None
        assert len(business_type_fields) == 1
        assert business_type_fields[0]["value"] == [{"id": 46}]
