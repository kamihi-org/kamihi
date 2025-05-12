"""
Custom views for the admin interface.

License:
    MIT

"""

from typing import Any, Literal

from starlette.requests import Request
from starlette_admin.contrib.mongoengine import ModelView


class NoClsView(ModelView):
    """NoClsView hides the "_cls" field from the admin interface."""

    exclude_fields_from_list = ["_cls"]
    exclude_fields_from_detail = ["_cls"]
    exclude_fields_from_create = ["_cls"]
    exclude_fields_from_edit = ["_cls"]


class HooksView(NoClsView):
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

    async def before_create(self, request: Request, data: dict[str, Any], obj: Any) -> None:  # noqa: ANN401
        """Run before creating an object."""
        for hook in self.hooks.get("before_create", []):
            await hook(request, data, obj)

    async def after_create(self, request: Request, obj: Any) -> None:  # noqa: ANN401
        """Run after creating an object."""
        for hook in self.hooks.get("after_create", []):
            await hook(request, obj)

    async def before_edit(self, request: Request, data: dict[str, Any], obj: Any) -> None:  # noqa: ANN401
        """Run before editing an object."""
        for hook in self.hooks.get("before_edit", []):
            await hook(request, data, obj)

    async def after_edit(self, request: Request, obj: Any) -> None:  # noqa: ANN401
        """Run after editing an object."""
        for hook in self.hooks.get("after_edit", []):
            await hook(request, obj)

    async def before_delete(self, request: Request, obj: Any) -> None:  # noqa: ANN401
        """Run before deleting an object."""
        for hook in self.hooks.get("before_delete", []):
            await hook(request, obj)

    async def after_delete(self, request: Request, obj: Any) -> None:  # noqa: ANN401
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
