from config.urls import urlpatterns


class ZendeskAPIProxyMiddleware:
    """
    Proxies requests to Zendesk if we do not
    handle the endpoint used
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.api_urls = []
        # One-time configuration and initialization.

        for url_pattern in urlpatterns:
            # TODO create list of URL and HTTP verb
            pass

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        if request.url not in self.api_urls:
            # Proxy request - send on to Zendesk
            # Get auth from header?
            response = "what comes back from Zendesk API"

            # Maybe use HttpStreamingResponse

            # Raise Sentry error to tell us that this is happening

            # Give whatever status code, other request info back to the caller
        else:
            response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
