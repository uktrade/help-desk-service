from config.settings.base import *  # type: ignore # noqa

# DRF
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]
REST_FRAMEWORK["DEFAULT_PAGINATION_CLASS"] = "help_desk_api.pagination.CustomPagination"
REST_FRAMEWORK["PAGE_SIZE"] = 100
