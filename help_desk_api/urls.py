from django.urls import include, path

from help_desk_api.views import (
    CommentView,
    MeView,
    SingleTicketView,
    TicketView,
    UploadsView,
    UserView,
)

app_name = "help_desk_api"

"""
zenpy.Zenpy.tickets.create - POST /api/v2/tickets
zenpy.Zenpy.tickets - GET /api/v2/tickets/{id}
zenpy.Zenpy.tickets.update - PUT /api/v2/tickets/{id}
zenpy.Zenpy.tickets.comments - GET /api/v2/tickets/{id}/comments
zenpy.Zenpy.users - GET /api/v2/users/{id}
zenpy.Zenpy.users.create_or_update - POST /api/v2/users/create_or_update
zenpy.Zenpy.users.me - GET /api/v2/users/me
zenpy.Zenpy.uploads - POST /api/v2/uploads
"""

urlpatterns = [
    path(
        "",
        include(
            [
                path("v2/tickets.json", TicketView.as_view(), name="tickets"),
                path("v2/tickets/<int:id>.json", SingleTicketView.as_view(), name="ticket"),
                path("v2/tickets/<int:id>/comments.json", CommentView.as_view(), name="comments"),
                path("v2/users/<int:id>.json", UserView.as_view(), name="user"),
                path("v2/users/create_or_update.json", UserView.as_view(), name="create_user"),
                path("v2/users/me.json", MeView.as_view(), name="me"),  # /PS-IGNORE
                path("v2/uploads.json", UploadsView.as_view(), name="uploads"),  # /PS-IGNORE
            ]
        ),
    )
]
