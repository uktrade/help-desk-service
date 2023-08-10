import base64
import inspect
import json
import logging
import sys

import requests
from django.contrib.auth.hashers import check_password
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from rest_framework.exceptions import APIException
from rest_framework.views import APIView

# Needed for inspect
from help_desk_api import views  # noqa F401
from help_desk_api.models import HelpDeskCreds
from help_desk_api.serializers import ZendeskFieldsNotSupportedException
from help_desk_api.urls import urlpatterns as api_url_patterns
from help_desk_api.utils import get_zenpy_request_vars

logger = logging.getLogger(__name__)


def get_view_class(path):
    view_class = None

    for url_pattern in api_url_patterns[0].url_patterns:
        if url_pattern.pattern.match(path.replace("/api/", "")):
            view_class = url_pattern.lookup_str
            return view_class

    if not view_class:
        return False


def method_supported(path, method):
    view_class = get_view_class(path)

    for class_name, obj in inspect.getmembers(sys.modules["help_desk_api.views"]):
        try:
            if issubclass(obj, APIView):
                if class_name in view_class:
                    if method in obj().allowed_methods:
                        return True
        except TypeError:
            pass

    return False


def proxy_zendesk(request, subdomain, email, token, query_string):
    url = f"https://{subdomain}.zendesk.com{request.path}"

    if query_string:
        url = f"{url}?{query_string}"

    creds = f"{email}/token:{token}"
    encoded_creds = base64.b64encode(creds.encode("ascii"))  # /PS-IGNORE
    zendesk_response = None

    # Make request to Zendesk API
    content_type = request.headers.get("Content-Type", default="application/json")
    if request.method == "GET":  # /PS-IGNORE
        zendesk_response = requests.get(
            url,
            headers={
                "Authorization": f"Basic {encoded_creds.decode('ascii')}",  # /PS-IGNORE
                "Content-Type": content_type,
            },
        )
    # data=request.body.decode("utf8"),
    elif request.method == "POST":
        zendesk_response = requests.post(
            url,
            data=request.body,
            headers={
                "Authorization": f"Basic {encoded_creds.decode('ascii')}",
                "Content-Type": content_type,
            },
        )
    elif request.method == "PUT":
        zendesk_response = requests.put(
            url,
            data=request.body.decode("utf8"),
            headers={
                "Authorization": f"Basic {encoded_creds.decode('ascii')}",
                "Content-Type": content_type,
            },
        )

    return zendesk_response


class ZendeskAPIProxyMiddleware:
    """
    Proxies requests to Zendesk if we do not
    handle the endpoint used
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            # Get out of proxy logic if there's an issue with the token
            token, email = get_zenpy_request_vars(request)
        except APIException:
            return self.get_response(request)

        help_desk_creds = HelpDeskCreds.objects.get(zendesk_email=email)

        logger.debug(f"{token}, {help_desk_creds.zendesk_token}")
        if not check_password(token, help_desk_creds.zendesk_token):
            return HttpResponseServerError()

        zendesk_response = None
        django_response = None

        supported_endpoint = method_supported(request.path, request.method.upper())

        if HelpDeskCreds.HelpDeskChoices.ZENDESK in help_desk_creds.help_desk:
            zendesk_response = self.make_zendesk_request(
                help_desk_creds, request, token, supported_endpoint
            )

        if HelpDeskCreds.HelpDeskChoices.HALO in help_desk_creds.help_desk:
            try:
                django_response = self.make_halo_request(
                    help_desk_creds, request, supported_endpoint
                )
            except ZendeskFieldsNotSupportedException as e:
                logger.debug(f"BAD REQUEST: {e}")
                django_response = HttpResponseBadRequest(f"Incorrect payload: {e}", status=400)
        return zendesk_response or django_response

    def make_halo_request(self, help_desk_creds, request, supported_endpoint):
        django_response = None
        if supported_endpoint:
            setattr(request, "help_desk_creds", help_desk_creds)
            django_response = self.get_response(request)
        return django_response

    def make_zendesk_request(self, help_desk_creds, request, token, supported_endpoint):
        # Don't need to call the below in Halo because error will be raised anyway
        if not supported_endpoint:
            print("TODO raise Sentry error...")
        proxy_response = proxy_zendesk(
            request,
            help_desk_creds.zendesk_subdomain,
            help_desk_creds.zendesk_email,
            token,
            request.GET.urlencode(),
        )
        zendesk_response = HttpResponse(
            json.dumps(proxy_response.json(), cls=DjangoJSONEncoder),
            headers={
                "Content-Type": "application/json",
            },
            status=proxy_response.status_code,
        )
        # status, location, copy dict
        return zendesk_response
