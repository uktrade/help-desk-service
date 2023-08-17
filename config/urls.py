from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from help_desk_api import urls as help_desk_api_urls

# from rest_framework import permissions, renderers
# from rest_framework.schemas import get_schema_view

# from help_desk_api.schema import FullDisclosureSchemaGenerator


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(help_desk_api_urls, namespace="api")),
]

# path('openapi/ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
urlpatterns += [
    path("openapi/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "openapi/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("openapi/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
