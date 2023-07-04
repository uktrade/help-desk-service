from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from rest_framework import permissions, renderers
from rest_framework.schemas import get_schema_view

from help_desk_api import urls as help_desk_api_urls
from help_desk_api.schema import FullDisclosureSchemaGenerator

openapi_view_kwargs = {
    "title": settings.OPENAPI_CONFIG.get("title", ""),
    "description": settings.OPENAPI_CONFIG.get("description", "").strip(),
    "urlconf": help_desk_api_urls,  # /PS-IGNORE
    "permission_classes": [permissions.IsAuthenticatedOrReadOnly],
    "authentication_classes": [],
    "renderer_classes": [renderers.OpenAPIRenderer],
    "generator_class": FullDisclosureSchemaGenerator,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(help_desk_api_urls, namespace="api")),
    path(
        "openapi/",
        include(
            [
                path(
                    "",
                    get_schema_view(
                        **openapi_view_kwargs,
                    ),
                    name="openapi-schema-default",
                ),
                path(
                    "openapi.yaml",
                    get_schema_view(
                        **openapi_view_kwargs,
                    ),
                    name="openapi-schema-yaml",
                ),
                path(
                    "openapi.yml",
                    get_schema_view(
                        **openapi_view_kwargs,
                    ),
                    name="openapi-schema-yml",
                ),
                path(
                    "openapi.json",
                    get_schema_view(
                        **openapi_view_kwargs
                        | {"renderer_classes": [renderers.JSONOpenAPIRenderer]}
                    ),
                    name="openapi-schema-json",
                ),
            ]
        ),
    ),
]
