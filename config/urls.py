from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from rest_framework import permissions, renderers
from rest_framework.schemas import get_schema_view

from help_desk_api import urls as help_desk_api_urls
from help_desk_api.schema import FullDisclosureSchemaGenerator

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

'''
openapi_view_kwargs = {
    "title": settings.OPENAPI_CONFIG.get("title", ""),
    "description": settings.OPENAPI_CONFIG.get("description", "").strip(),
    "urlconf": help_desk_api_urls,  # /PS-IGNORE
    "permission_classes": [permissions.IsAuthenticatedOrReadOnly],
    "authentication_classes": [],
    "renderer_classes": [renderers.OpenAPIRenderer],
    "generator_class": FullDisclosureSchemaGenerator,
}
'''

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(help_desk_api_urls, namespace="api")),
    
]

#path('openapi/ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
urlpatterns += [
    path('openapi/', SpectacularAPIView.as_view(), name='schema'),
    path(
        "openapi/swagger-ui/",
        SpectacularSwaggerView.as_view(
            template_name="swagger-ui.html", url_name="schema"
        ),
        name="swagger-ui",
    ),
    #path('openapi/ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('openapi/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]

'''
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
'''
