#from rest_framework.schemas.openapi import SchemaGenerator
from drf_spectacular.generators import SchemaGenerator


class FullDisclosureSchemaGenerator(SchemaGenerator):
    """
    Allows OpenAPI schema generator views to access all views.

    The default implementation only examines APIViews which
    the client requesting the OpenAPI schema has permission to access.
    All API endpoints use help_desk_api.auth.ZenpyAuthentication, but
    it is not practical to require the client to authenticate
    in that way to view the schema. Therefore, permit access to all views.
    """

    def has_view_permissions(self, path, method, view):
        return True
