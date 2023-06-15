
from unittest import mock
import pytest

from django.test import Client
from django.urls import reverse
from http import HTTPStatus
from requests import Response


class TestSupportedOperations:
    '''
    The following @mock.patch lines ensure the external services don't actually
    have requests made to them by the test.
    '''

    @mock.patch("zendesk_api_proxy.middleware.proxy_zendesk")
    def test_update_ticket_by_id(
        self,
        proxy_zendesk: mock.MagicMock, 
        client: Client,
        zendesk_required_settings, # fixture: see /tests/conftest.py
        zendesk_creds_only,
        zendesk_authorization_header
    ):
        ticket_id = 123
        created_at = '2018-01-28T14:50:32Z'
        subject = 'Any subject'
        priority = 'Low'
        status = 'pending'
        requester_id = 18655244625

        data = {
            "description": "A description",
        }

        url = reverse("api:ticket", kwargs={"id": 123})
        
        response = Response()
        response._content = b"{}"
        response.status_code = HTTPStatus.OK
        
        proxy_zendesk.return_value = response
        
        client.put(url, data=data, headers={"Authorization": zendesk_authorization_header})
        proxy_zendesk.assert_called_once() # make sure the middleware called the function
        
        client.get(url, headers={"Authorization": zendesk_authorization_header})
        proxy_zendesk.assert_called

        request = proxy_zendesk.call_args[0]
        
        
        #assert request.url == url # not sure about this - look up Request docs
        #assert request.data == data
        #assert request.method == "PUT"
      