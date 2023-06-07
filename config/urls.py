from django.contrib import admin
from django.urls import include, path

from help_desk_api import urls as help_desk_api_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(help_desk_api_urls, namespace="api")),
]
