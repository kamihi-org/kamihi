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


class ActionView(ModelView):
    """ActionView is a custom view for the Action model in the admin interface."""

    exclude_fields_from_edit = ["name", "commands", "description"]

    def can_delete(self, request: Request) -> bool:  # noqa: ARG002
        """
        Override to prevent deletion of the Action model.

        Args:
            request (Request): The request object.

        """
        return False

    def can_create(self, request: Request) -> bool:  # noqa: ARG002
        """
        Override to prevent creation of the Action model.

        Args:
            request (Request): The request object.

        """
        return False
