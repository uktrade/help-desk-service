from http import HTTPStatus

from django.views.generic import TemplateView

from help_desk_api.models import HelpDeskCreds


class HealthCheckView(TemplateView):
    template_name = "healthcheck/healthcheck.xml"
    content_type = "text/xml"
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        status_code = self.get_status_code()
        context = self.get_context_data(status_code=status_code.value, **kwargs)
        return self.render_to_response(context, status=status_code)

    def get_status_code(self):
        try:
            # Check that we can connect to the database
            records = HelpDeskCreds.objects.all()
            # force evaluation of the queryset
            bool(records)
        except Exception:
            return HTTPStatus.SERVICE_UNAVAILABLE
        return HTTPStatus.OK
