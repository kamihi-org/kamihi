"""
Custom views for the admin interface.

License:
    MIT

"""

from starlette.requests import Request
from starlette_admin.contrib.mongoengine import ModelView


class NoClsView(ModelView):
    """NoClsView hides the "_cls" field from the admin interface."""

    exclude_fields_from_list = ["_cls"]
    exclude_fields_from_detail = ["_cls"]
    exclude_fields_from_create = ["_cls"]
    exclude_fields_from_edit = ["_cls"]


class ReadOnlyView(ModelView):
    """ReadOnlyView makes the model read-only in the admin interface."""

    def can_create(self, request: Request) -> bool:  # noqa: ARG002
        """Check if the user can create a new instance of the model."""
        return False

    def can_edit(self, request: Request) -> bool:  # noqa: ARG002
        """Check if the user can edit an instance of the model."""
        return False

    def can_delete(self, request: Request) -> bool:  # noqa: ARG002
        """Check if the user can edit an instance of the model."""
        return False
