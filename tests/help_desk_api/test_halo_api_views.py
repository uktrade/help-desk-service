from unittest import mock

from halo.halo_manager import HaloManager

from help_desk_api.views import HaloBaseView


class TestHaloApiViews:
    def test_base_api_view_has_halo_manager(self, halo_get_tickets_request):
        with mock.patch(
            "halo.halo_manager.HaloAPIClient._HaloAPIClient__authenticate"
        ):  # /PS-IGNORE
            view = HaloBaseView()

            view.initial(halo_get_tickets_request)

        assert hasattr(view, "halo_manager")
        assert view.halo_manager is not None
        assert isinstance(view.halo_manager, HaloManager)
