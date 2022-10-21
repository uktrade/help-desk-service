from django.urls import path

from help_desk_api.views import TicketView

urlpatterns = [
    path("v2/tickets.json", TicketView.as_view(), name="ticket"),
]
