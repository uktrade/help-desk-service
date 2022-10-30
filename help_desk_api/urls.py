from django.urls import path

from help_desk_api.views import CommentView, MeView, TicketView, UserView

"""
zenpy.Zenpy.tickets.create - POST /api/v2/tickets
zenpy.Zenpy.tickets - GET /api/v2/tickets/{id}
zenpy.Zenpy.tickets.update - PUT /api/v2/tickets/{id}
zenpy.Zenpy.tickets.comments - GET /api/v2/tickets/{id}/comments
zenpy.Zenpy.users - GET /api/v2/users/{id}
zenpy.Zenpy.users.create_or_update - POST /api/v2/users/create_or_update
zenpy.Zenpy.users.me - GET /api/v2/users/me
"""

urlpatterns = [
    path("v2/tickets.json", TicketView.as_view(), name="tickets"),
    path("v2/tickets/<int:id>.json", TicketView.as_view(), name="ticket"),
    path("v2/tickets/<int:id>/comments.json", CommentView.as_view(), name="comments"),
    path("v2/users/<int:id>.json", UserView.as_view(), name="user"),
    path("v2/users/create_or_update.json", UserView.as_view(), name="crete_user"),
    path("v2/users/me.json", MeView.as_view(), name="me"),
]
