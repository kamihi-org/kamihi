"""
Custom views for the admin interface.

License:
    MIT

"""

from typing import Any, Literal

from starlette.requests import Request
from starlette_admin.contrib.sqla import ModelView
from starlette_admin.exceptions import FormValidationError

from kamihi.base.utils import is_valid_cron_expression


class ExcludeIDModelView(ModelView):
    """ExcludeIDModelView is a custom view that excludes the ID field from forms."""

    exclude_fields_from_list = ["id"]
    exclude_fields_from_detail = ["id"]
    exclude_fields_from_create = ["id"]
    exclude_fields_from_edit = ["id"]


class HooksView(ExcludeIDModelView):
    """HooksView is a custom view that accepts a dictionary of hooks on different events."""

    hooks: dict[
        Literal[
            "before_create",
            "after_create",
            "before_edit",
            "after_edit",
            "before_delete",
            "after_delete",
        ],
        list[callable],
    ]

    def __init__(self, *args, hooks: dict = None, **kwargs) -> None:  # noqa: ANN002, ANN003
        """
        Initialize the HooksView with hooks.

        Args:
            *args: Positional arguments.
            hooks (dict): A dictionary of hooks for different events.
            **kwargs: Keyword arguments.

        """
        super().__init__(*args, **kwargs)
        self.hooks = hooks or {}

    async def before_create(self, request: Request, data: dict[str, Any], obj: Any) -> None:
        """Run before creating an object."""
        for hook in self.hooks.get("before_create", []):
            await hook(request, data, obj)

    async def after_create(self, request: Request, obj: Any) -> None:
        """Run after creating an object."""
        for hook in self.hooks.get("after_create", []):
            await hook(request, obj)

    async def before_edit(self, request: Request, data: dict[str, Any], obj: Any) -> None:
        """Run before editing an object."""
        for hook in self.hooks.get("before_edit", []):
            await hook(request, data, obj)

    async def after_edit(self, request: Request, obj: Any) -> None:
        """Run after editing an object."""
        for hook in self.hooks.get("after_edit", []):
            await hook(request, obj)

    async def before_delete(self, request: Request, obj: Any) -> None:
        """Run before deleting an object."""
        for hook in self.hooks.get("before_delete", []):
            await hook(request, obj)

    async def after_delete(self, request: Request, obj: Any) -> None:
        """Run after deleting an object."""
        for hook in self.hooks.get("after_delete", []):
            await hook(request, obj)


class ReadOnlyView(HooksView):
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


class JobView(HooksView):
    """JobView is a custom view for managing jobs in the admin interface."""

    async def validate(self, request: Request, data: dict[str, Any]) -> None:
        """Validate the job data before creating or editing."""
        errors: dict[str, str] = {}

        if not is_valid_cron_expression(data["cron_expression"]):
            errors["cron_expression"] = "Invalid cron expression."

        if len(errors) > 0:
            raise FormValidationError(errors)
        return await super().validate(request, data)
