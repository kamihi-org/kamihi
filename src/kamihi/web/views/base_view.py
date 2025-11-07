"""
BaseView for Starlette-Admin with hooks for CRUD operations.

License:
    MIT

"""

import inspect
from collections.abc import Callable
from typing import Any, Literal

from starlette.requests import Request
from starlette_admin.contrib.sqla import ModelView


class BaseView(ModelView):
    """HooksView is a custom view that accepts a dictionary of hooks on different events."""

    exclude_fields_from_list = ["id"]
    exclude_fields_from_detail = ["id"]
    exclude_fields_from_create = ["id"]
    exclude_fields_from_edit = ["id"]

    hooks: dict[
        Literal[
            "before_create",
            "after_create",
            "before_edit",
            "after_edit",
            "before_delete",
            "after_delete",
        ],
        list[Callable],
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

    async def _run_hooks(self, hook_list: list[Callable], *args: Any) -> None:
        """Run a list of hooks with the given arguments."""
        for hook in hook_list:
            if inspect.iscoroutinefunction(hook):
                await hook(*args)
            else:
                hook(*args)

    async def before_create(self, request: Request, data: dict[str, Any], obj: Any) -> None:
        """Run before creating an object."""
        await self._run_hooks(self.hooks.get("before_create", []), request, data, obj)

    async def after_create(self, request: Request, obj: Any) -> None:
        """Run after creating an object."""
        await self._run_hooks(self.hooks.get("after_create", []), request, obj)

    async def before_edit(self, request: Request, data: dict[str, Any], obj: Any) -> None:
        """Run before editing an object."""
        await self._run_hooks(self.hooks.get("before_edit", []), request, data, obj)

    async def after_edit(self, request: Request, obj: Any) -> None:
        """Run after editing an object."""
        await self._run_hooks(self.hooks.get("after_edit", []), request, obj)

    async def before_delete(self, request: Request, obj: Any) -> None:
        """Run before deleting an object."""
        await self._run_hooks(self.hooks.get("before_delete", []), request, obj)

    async def after_delete(self, request: Request, obj: Any) -> None:
        """Run after deleting an object."""
        await self._run_hooks(self.hooks.get("after_delete", []), request, obj)
