from help_desk_api.serializers import ZendeskToHaloCreateTicketSerializer


class TestDataWorkspaceTickets:
    def test_dataset_access_request_initial(self, dataset_access_request_initial):
        serialiser = ZendeskToHaloCreateTicketSerializer()

        halo_equivalent = serialiser.to_representation(dataset_access_request_initial["ticket"])

        assert halo_equivalent is not None
