from typing import OrderedDict

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    """
    A simple page number based style that supports page numbers as
    query parameters. For example:

    http://zendesk.com/api?page=2
    """

    template = "rest_framework/pagination/numbers.html"

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("next_page", self.get_next_link()),
                    ("previous_page", self.get_previous_link()),
                    ("count", self.page.paginator.count),
                    ("tickets", data["tickets"]),
                ]
            )
        )
