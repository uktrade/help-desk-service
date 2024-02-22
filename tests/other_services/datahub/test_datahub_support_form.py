# from http import HTTPStatus  /PS-IGNORE
# from unittest import skip
#
# from django.test import RequestFactory  /PS-IGNORE
# from django.urls import reverse
# from zendesk_api_proxy.middleware import proxy_zendesk
#
# from help_desk_api.models import HelpDeskCreds  /PS-IGNORE


class TestDatahubSupportForm:
    pass
    # @skip("Test once we've mocked the response")
    # def test_zendesk_only(
    #     self,
    #     # mock_post,
    #     zendesk_authorization_header: str,
    #     rf: RequestFactory,  /PS-IGNORE
    #     zendesk_required_settings,
    #     datahub_zendesk_creds_only: HelpDeskCreds,
    #     datahub_frontend_support_ticket,
    # ):
    #     request = rf.post(
    #         reverse("api:tickets"),
    #         data=datahub_frontend_support_ticket,
    #         HTTP_AUTHORIZATION=zendesk_authorization_header,
    #         content_type="application/json",
    #     )
    #
    #     response = proxy_zendesk(
    #         request,
    #         datahub_zendesk_creds_only.zendesk_subdomain,
    #         datahub_zendesk_creds_only.zendesk_email,
    #         datahub_zendesk_creds_only.zendesk_token,
    #         "",
    #     )
    #
    #     assert response.status_code == HTTPStatus.OK  /PS-IGNORE
    #     # mock_post.assert_called_once()
