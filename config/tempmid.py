import logging

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")


def add_request_logging_middleware(get_response):
    def middleware(request):
        logger.debug(request)
        response = get_response(request)
        return response

    return middleware
