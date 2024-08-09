import base64
import inspect
import json
import logging
import sys
import traceback
from http import HTTPStatus

import requests
import sentry_sdk
from django.conf import settings
from django.contrib.auth.hashers import check_password
from django.core.cache import caches
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.urls import ResolverMatch, resolve
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
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
        logger.error(f"Zendesk GET: {url}")
        zendesk_response = requests.get(
            url,
            headers={
                "Authorization": f"Basic {encoded_creds.decode('ascii')}",  # /PS-IGNORE
                "Content-Type": content_type,
            },
        )
        logger.error("Completed Zendesk GET")
    # data=request.body.decode("utf8"),
    elif request.method == "POST":
        logger.warning(f"POST: {request.body}")
        logger.warning(f"Auth: {encoded_creds.decode('ascii')}")
        logger.error(f"Zendesk POST: {url}")
        zendesk_response = requests.post(
            url,
            data=request.body,
            headers={
                "Authorization": f"Basic {encoded_creds.decode('ascii')}",
                "Content-Type": content_type,
            },
        )
        logger.error("Completed Zendesk POST")
    elif request.method == "PUT":
        logger.error(f"Zendesk PUT: {url}")
        zendesk_response = requests.put(
            url,
            data=request.body.decode("utf8"),
            headers={
                "Authorization": f"Basic {encoded_creds.decode('ascii')}",
                "Content-Type": content_type,
            },
        )
        logger.error("Completed Zendesk PUT")

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

        logger.info(f"Help Desk Service request received, body: {request_body}")

        try:
            help_desk_creds, token = self.get_authentication_values(request)
        except AuthenticationFailed as exp:
            sentry_sdk.capture_exception(exp)
            raise
        except NotAuthenticated:
            return self.get_response(request)

        logger.info(
            f"HelpDeskCreds: {help_desk_creds.pk} "
            f"for zendesk_email: {help_desk_creds.zendesk_email}"
        )

        zendesk_response = None
        django_response = None

        supported_endpoint = method_supported(request.path, request.method.upper())

        logger.info(
            f"Supported endpoint {request.path}: {'true' if supported_endpoint else 'false'}"
        )

        if HelpDeskCreds.HelpDeskChoices.ZENDESK in help_desk_creds.help_desk:
            logger.info("Making Zendesk request")
            zendesk_response = self.make_zendesk_request(
                help_desk_creds, request, token, supported_endpoint
            )

        if HelpDeskCreds.HelpDeskChoices.HALO in help_desk_creds.help_desk:
            try:
                """
                We wrap this in try-catch so we can prevent any Halo errors
                getting back to the requester when dual-running, as only
                Zendesk errors should be returned to them.
                The whole idea of dual-running is that if
                Zendesk succeeds but Halo fails, Zendesk wins.
                """
                logger.info("Making Halo request")  # /PS-IGNORE
                # Need to pass Zendesk ticket ID, if any
                zendesk_response_json = self.get_json_response(zendesk_response, {})
                zendesk_ticket = zendesk_response_json.get("ticket", {})
                zendesk_ticket_id = zendesk_ticket.get("id", None)
                setattr(request, "zendesk_ticket_id", zendesk_ticket_id)
                try:
                    django_response = self.make_halo_request(
                        help_desk_creds, request, supported_endpoint
                    )
                except ZendeskFieldsNotSupportedException as exp:
                    sentry_sdk.capture_exception(exp)
                    django_response = JsonResponse(
                        {"error": f"Incorrect payload: {exp}"}, status=HTTPStatus.BAD_REQUEST
                    )
            except Exception as exp:
                """
                We catch Exception as this needs to be as broad as possible,
                to prevent Halo errors getting back when Zendesk is enabled.
                """
                sentry_sdk.capture_exception(exp)
                django_response = JsonResponse(
                    {
                        "error": str(exp),
                    },
                    status=HTTPStatus.INTERNAL_SERVER_ERROR,
                )
        # If this is /api/v2/users/create_or_update,
        # we need to save the Zendesk request data under the user ID
        # as there's no other way to map the latter to the former
        # on a subsequent create_ticket request
        resolver: ResolverMatch = resolve(request.path)
        if resolver.url_name == "create_user":
            self.cache_request_data(
                request,
                help_desk_creds,
                zendesk_response,
                django_response,
                {"cache_name": settings.USER_DATA_CACHE, "datum_keys": ("user", "id")},
            )
        elif resolver.url_name in ("tickets",) and request.method.upper() != "GET":
            self.cache_request_data(
                request,
                help_desk_creds,
                zendesk_response,
                django_response,
                {"cache_name": settings.TICKET_DATA_CACHE, "datum_keys": ("ticket", "id")},
            )
        elif resolver.url_name == "uploads":
            self.cache_request_data(
                request,
                help_desk_creds,
                zendesk_response,
                django_response,
                {"cache_name": settings.UPLOAD_DATA_CACHE, "datum_keys": ("upload", "token")},
            )
        logger.warning(
            f"Zendesk response: {zendesk_response.content.decode('utf-8') if zendesk_response else None}"  # noqa:E501
        )
        logger.warning(
            f"Halo response: {django_response.content.decode('utf-8') if django_response else None}"
        )
        return zendesk_response or django_response

    def get_authentication_values(self, request):
        # Get out of proxy logic if there's an issue with the token
        # get_zenpy_request_vars raises NotAuthenticated
        # if no Authorization header found
        logger.debug("Zenpy vars from request")
        token, email = get_zenpy_request_vars(request)
        logger.debug(f"Get HelpDeskCreds for {email}")
        help_desk_creds_for_email = HelpDeskCreds.objects.filter(zendesk_email=email)
        if not help_desk_creds_for_email:
            raise AuthenticationFailed(detail=f"Credentials not valid for {email}")
        logger.debug("Search HelpDeskCreds for matching set")
        matching_help_desk_creds = None
        for help_desk_creds in help_desk_creds_for_email:
            logger.debug("Call check_password")
            if check_password(token, help_desk_creds.zendesk_token):
                logger.debug("Found matching credentials")
                matching_help_desk_creds = help_desk_creds
                break
        if matching_help_desk_creds is None:
            logger.debug("Failed to find matching credentials")
            raise AuthenticationFailed(detail=f"Credentials not valid for {email}")
        logger.debug("Return matching credentials")
        return matching_help_desk_creds, token

    def cache_request_data(
        self, request, help_desk_creds, zendesk_response, halo_response, cache_config
    ):
        """
        Cache request data for create_or_update user and create_ticket.
        This is necessary as D-F-API gets the user in one request,
        then creates the ticket for that user in a separate request
        which only contains the user ID.
        Meanwhile, Data Workspace creates the ticket then adds a comment to it.
        The z-to-h serializer thus needs a way to associate a Zendesk ID
        with a Halo record.
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
        logger.info(
            f"Cacheing {cache_config['datum_keys']} with services: {help_desk_creds.help_desk}"
        )
        logger.info(f"Cacheing response: {zendesk_response_json}")
        cache_key = self.get_cache_key_for_credentials(
            zendesk_response_json, halo_response_json, help_desk_creds, cache_config["datum_keys"]
        )
        if cache_key is None:
            # This should never happen if we got here, so just bail for now
            sentry_sdk.capture_message(f"Failed to get {cache_config['datum_keys']} for cacheing")
            return
        cache_name = cache_config["cache_name"]
        cache = caches[cache_name]
        if cache is not None:
            # This conditional is a bit of a code smell :-/
            if cache_name == settings.USER_DATA_CACHE:
                request_data = json.loads(request.body.decode("utf-8"))
                logger.info(
                    f"Cacheing {cache_config['datum_keys']} "
                    f"with key: {cache_key} data: {request_data}"
                )
                cache.set(cache_key, request_data)
            elif halo_response_json and "ticket" in halo_response_json:
                halo_ticket_id = halo_response_json["ticket"]["id"]
                logger.info(
                    f"Cacheing {cache_config['datum_keys']} "
                    f"with key: {cache_key} data: {halo_ticket_id}"
                )
                cache.set(cache_key, halo_ticket_id)
            elif halo_response_json and "upload" in halo_response_json:
                halo_upload_token = halo_response_json["upload"]["token"]
                logger.info(
                    f"Cacheing {cache_config['datum_keys']} "
                    f"with key: {cache_key} data: {halo_upload_token}"
                )
                cache.set(cache_key, halo_upload_token)

    def get_cache_key_for_credentials(
        self, zendesk_response_json, halo_response_json, help_desk_creds, datum_keys=("user", "id")
    ):
        cache_key = None
        if HelpDeskCreds.HelpDeskChoices.ZENDESK in help_desk_creds.help_desk:
            # Use the Zendesk user ID as the cache key
            # because that is what we'll get in the create_ticket request
            cache_key = self.get_cache_key(zendesk_response_json, datum_keys)
            logger.info(f"Zendesk {datum_keys} cache key: {cache_key}")
        elif HelpDeskCreds.HelpDeskChoices.HALO in help_desk_creds.help_desk:
            # Use the Halo user ID as the cache key
            # as if there's no Zendesk request, that's what will end up coming back
            # in the subsequent create_ticket request
            cache_key = self.get_cache_key(halo_response_json, datum_keys)
            logger.info(f"Halo {datum_keys} cache key: {cache_key}")
        return cache_key

    def get_cache_key(self, response_json, datum_keys=("user", "id")):
        datum = response_json.get(datum_keys[0], {})
        cache_key = datum.get(datum_keys[1], None)
        return cache_key

    def get_json_responses(self, halo_response, zendesk_response):
        return self.get_json_response(halo_response), self.get_json_response(zendesk_response)

    def get_json_response(self, response, default=None):
        return json.loads(response.content.decode("utf-8")) if response else default

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

    def process_exception(self, request: HttpRequest, exception):
        if request.content_type != "application/json":
            return None
        response_content = {
            "error": f"{type(exception)}: {exception}",
        }
        exc_info = sys.exc_info()
        stack_trace = traceback.format_exception(*exc_info)
        debug_content = {
            "traceback": stack_trace,
        }
        response_content.update(**debug_content)
        return JsonResponse(response_content, status=HTTPStatus.INTERNAL_SERVER_ERROR)
