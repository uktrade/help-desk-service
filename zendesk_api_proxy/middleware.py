import inspect
import sys

import requests
from dit_team.models import HALO, ZENDESK
from django.http import HttpResponse
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

# Needed for inspect
from help_desk_api import views  # noqa F401
from help_desk_api.urls import urlpatterns as api_url_patterns
from help_desk_api.utils import get_request_token


def has_endpoint(url, method):
    view_class = None

    for url_pattern in api_url_patterns:
        if url_pattern.pattern.match(url.replace("api/", "")):
            view_class = url_pattern.lookup_str

    if not view_class:
        return False

    for class_name, obj in inspect.getmembers(sys.modules["help_desk_api.views"]):
        try:
            if issubclass(obj, APIView):
                if class_name in view_class:
                    # print(f"url us {url}")
                    # print(f"class is {class_name}")
                    # print(f"allowed methods are {obj().allowed_methods}")

                    if method in obj().allowed_methods:
                        return True
        except TypeError:
            pass

    return False


def proxy_zendesk(request):
    if not has_endpoint(request.url, request.method.upper()):
        print("Raise Sentry error")

    token = get_request_token(request)

    # Do the HTTP get request
    if request.method == "get":
        zendesk_response = requests.get(request.url, headers={"Authorization": f"Bearer {token}"})
    elif request.method == "post":
        zendesk_response = requests.post(
            request.url, json=request.body, headers={"Authorization": f"Bearer {token}"}
        )

    # Check for HTTP codes other than 200
    if zendesk_response.status_code != 200:
        print("Status:", zendesk_response.status_code, "Problem with the request. Exiting.")
        # TODO specific error
        Exception("Non 200 back from Zendesk API")
    else:
        return zendesk_response.json()


class ZendeskAPIProxyMiddleware:
    """
    Proxies requests to Zendesk if we do not
    handle the endpoint used
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        token_string = get_request_token(request)
        team_token = Token.objects.get(key=token_string)

        zendesk_response = None
        django_response = None

        # TODO check how token is wired up to custom user model
        if ZENDESK in team_token.user.help_desk.choices:
            # Don't need to call the below in Halo because error will be raised anyway
            if not has_endpoint(request.url, request.method.upper()):
                print("Raise Sentry error")

            zendesk_response_json = proxy_zendesk(request)
            zendesk_response = HttpResponse(
                zendesk_response_json,
                headers={
                    "Content-Type": "application/json",
                },
            )

        if HALO in team_token.user.help_desk.choices:
            django_response = self.get_response(request)

        return zendesk_response or django_response
