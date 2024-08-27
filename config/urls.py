import healthcheck.urls
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from help_desk_api import urls as help_desk_api_urls
from help_desk_api.views import DownloadView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(healthcheck.urls.urlpatterns)),
    path("api/", include(help_desk_api_urls, namespace="api")),
    path("openapi/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "openapi/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("openapi/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("dl/", DownloadView.as_view(), name="dl"),
]
