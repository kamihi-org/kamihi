"""
Actions view module.

License:
    MIT

"""

from starlette.requests import Request

from .base_view import BaseView


class ActionView(BaseView):
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
