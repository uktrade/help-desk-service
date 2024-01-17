import time


class StatsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def process_request(self, request):
        request.start_time = time.time()

    def process_template_response(self, request, response):
        response_time = time.time() - request.start_time
        response.context_data["response_time"] = response_time
        response["Cache-Control"] = "no-cache, no-store, must-revalidate"  # /PS-IGNORE
        return response
