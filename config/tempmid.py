import logging

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


def add_request_logging_middleware(get_response):
    def middleware(request):
        logger.debug(request.headers)
        response = get_response(request)
        logger.debug(response.headers)
        return response

    return middleware
