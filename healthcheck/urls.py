from django.urls import path
from django.utils.decorators import decorator_from_middleware

from .middleware import StatsMiddleware
from .views import HealthCheckView

urlpatterns = [
    path(
        "healthcheck/",
        decorator_from_middleware(StatsMiddleware)(HealthCheckView.as_view()),
        name="healthcheck",
    )
]
