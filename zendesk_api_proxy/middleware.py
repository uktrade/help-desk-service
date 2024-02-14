import base64
import inspect
import json
import logging
import sys

import requests
import sentry_sdk
from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.core.cache import caches
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django.urls import ResolverMatch, resolve
from rest_framework.exceptions import APIException
from rest_framework.views import APIView
from sentry_sdk import set_level

# Needed for inspect
from help_desk_api import views  # noqa F401
from help_desk_api.models import HelpDeskCreds
from help_desk_api.serializers import ZendeskFieldsNotSupportedException
from help_desk_api.urls import urlpatterns as api_url_patterns
from help_desk_api.utils import get_zenpy_request_vars

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")

set_level("info")


def get_view_class(path):
    view_class = None

    for url_pattern in api_url_patterns[0].url_patterns:
        if url_pattern.pattern.match(path.replace("/api/", "")):
            view_class = url_pattern.lookup_str
            return view_class

    if not view_class:
        return False


def method_supported(path, method: str):
    logger.info(f"method_supported called with: {path}, {method}")
    view_class = get_view_class(path)
    logger.info(f"method_supported: view_class {view_class}")

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

    logger.warning(f"proxy_zendesk: requesting {url}")

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
        logger.warning(f"POST: {request.body}")
        logger.warning(f"Auth: {encoded_creds.decode('ascii')}")
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

    def __call__(self, request):  # noqa: C901
        try:
            request_body = request.body.decode("utf-8")
        except Exception as exp:
            sentry_sdk.capture_exception(exp)
            request_body = request.body

        logger.warning(f"Help Desk Service request received, body: {request_body}")

        try:
            # Get out of proxy logic if there's an issue with the token
            token, email = get_zenpy_request_vars(request)
        except APIException as exp:
            sentry_sdk.capture_exception(exp)
            return self.get_response(request)

        help_desk_creds = HelpDeskCreds.objects.get(zendesk_email=email)

        logger.info(f"HelpDeskCreds: {help_desk_creds.pk}")
        logger.info(f"zendesk_email: {help_desk_creds.zendesk_email}")

        if not check_password(token, help_desk_creds.zendesk_token):
            return HttpResponseServerError()

        logger.warning("check_password passed")

        zendesk_response = None
        django_response = None

        supported_endpoint = method_supported(request.path, request.method.upper())

        logger.warning(f"Supported endpoint: {'true' if supported_endpoint else 'false'}")

        if HelpDeskCreds.HelpDeskChoices.ZENDESK in help_desk_creds.help_desk:
            logger.info("Making Zendesk request")
            zendesk_response = self.make_zendesk_request(
                help_desk_creds, request, token, supported_endpoint
            )

        if HelpDeskCreds.HelpDeskChoices.HALO in help_desk_creds.help_desk:
            logger.info("Making Halo request")  # /PS-IGNORE
            try:
                django_response = self.make_halo_request(
                    help_desk_creds, request, supported_endpoint
                )
            except ZendeskFieldsNotSupportedException as exp:
                sentry_sdk.capture_exception(exp)
                django_response = HttpResponseBadRequest(f"Incorrect payload: {exp}", status=400)
        # If this is /api/v2/users/create_or_update,
        # we need to save the Zendesk request data under the user ID
        # as there's no other way to map the latter to the former
        # on a subsequent create_ticket request
        resolver: ResolverMatch = resolve(request.path)
        if resolver.url_name == "create_user":
            self.cache_user_request_data(
                request, help_desk_creds, zendesk_response, django_response
            )
        logger.warning(
            f"Zendesk response: {zendesk_response.content.decode('utf-8') if zendesk_response else None}"  # noqa:E501
        )
        logger.warning(
            f"Halo response: {django_response.content.decode('utf-8') if django_response else None}"
        )
        return zendesk_response or django_response

    def cache_user_request_data(self, request, help_desk_creds, zendesk_response, halo_response):
        """
        Cache request data for create_or_update user.
        This is necessary as D-F-API gets the user in one request,
        then creates the ticket for that user in a separate request
        which only contains the user ID.
        The z-to-h serializer thus needs a way to associate a Zendesk user ID
        with a Halo user.
        As Halo allows us to just specify the email and name in the ticket creation request,
        being able to map the created Zendesk ID to that data will do.
        In the case of Halo-only running, the Halo user ID will serve the same purpose,
        i.e. the serializer won't know or care that it's using a Halo ID;
        it just wants the data associated with the ID that got sent back to the requester
        and which the requester then sent back in the create_ticket request.
        """
        halo_response_json, zendesk_response_json = self.get_json_responses(
            halo_response, zendesk_response
        )
        logger.info(f"help_desk_creds: {help_desk_creds}")
        logger.info(f"cache_user_request_data: {zendesk_response_json}")
        cache_key = None
        if HelpDeskCreds.HelpDeskChoices.ZENDESK in help_desk_creds.help_desk:
            # Use the Zendesk user ID as the cache key
            # because that is what we'll get in the create_ticket request
            cache_key = self.get_cache_key(zendesk_response_json.get("user", {}))
            logger.info(f"Zendesk user cache key: {cache_key}")
            if cache_key is None:
                # This should never happen, so just bail for now
                sentry_sdk.capture_message("Failed to get user from cache (Zendesk branch)")
                return
        elif HelpDeskCreds.HelpDeskChoices.HALO in help_desk_creds.help_desk:
            # Use the Halo user ID as the cache key
            # as if there's no Zendesk request, that's what will end up coming back
            # in the subsequent create_ticket request
            cache_key = self.get_cache_key(halo_response_json.get("user", {}))
            logger.info(f"Halo user cache key: {cache_key}")
            if cache_key is None:
                # This should never happen if we got here, so just bail for now
                sentry_sdk.capture_message("Failed to get user from cache (Halo branch)")
                return
        request_data = json.loads(request.body.decode("utf-8"))
        cache = caches[settings.USER_DATA_CACHE]
        if cache is not None:
            logger.info(f"Cacheing user with key: {cache_key} data: {request_data}")
            cache.set(cache_key, request_data)

    def get_cache_key(self, response_json):
        cache_key = response_json.get("id", None)
        return cache_key

    def get_json_responses(self, halo_response, zendesk_response):
        if zendesk_response:
            zendesk_response_json = json.loads(zendesk_response.content.decode("utf-8"))
        else:
            zendesk_response_json = None
        if halo_response:
            halo_response_json = json.loads(halo_response.content.decode("utf-8"))
        else:
            halo_response_json = None
        return halo_response_json, zendesk_response_json

    def make_halo_request(self, help_desk_creds, request, supported_endpoint):
        django_response = None
        if supported_endpoint:
            setattr(request, "help_desk_creds", help_desk_creds)
            django_response = self.get_response(request)
            logger.info(
                f"""
            halo response status: {django_response.status_code}
             with body: {django_response.content}
            """
            )
        return django_response

    def make_zendesk_request(self, help_desk_creds, request, token, supported_endpoint):
        # Don't need to call the below in Halo because error will be raised anyway
        if not supported_endpoint:
            logger.warning(f"{request.path} is not supported by this service")
        proxy_response = proxy_zendesk(
            request,
            help_desk_creds.zendesk_subdomain,
            help_desk_creds.zendesk_email,
            token,
            request.GET.urlencode(),
        )
        logger.info(
            f"""
        proxy_zendesk response status: {proxy_response.status_code}
         with body: {proxy_response.content}
        """
        )
        zendesk_response = HttpResponse(
            json.dumps(proxy_response.json(), cls=DjangoJSONEncoder),
            headers={
                "Content-Type": "application/json",
            },
            status=proxy_response.status_code,
        )

        return zendesk_response
