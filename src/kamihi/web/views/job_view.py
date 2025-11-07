"""
Job view module for Kamihi web application.

License:
    MIT

"""

from typing import Any

from starlette.requests import Request
from starlette_admin import StringField
from starlette_admin.exceptions import FormValidationError

from kamihi.base.utils import is_valid_cron_expression

from .base_view import BaseView


class JobView(BaseView):
    """JobView is a custom view for managing jobs in the admin interface."""

    fields = [
        "action",
        "enabled",
        "users",
        "roles",
        StringField(
            "cron_expression",
            help_text="Cron expression for scheduling the job. E.g., '*/5 * * * *' for every 5 minutes. "
            "You can use https://crontab.guru/ to help generate valid expressions.",
        ),
        "args",
    ]

    async def validate(self, request: Request, data: dict[str, Any]) -> None:
        """Validate the job data before creating or editing."""
        errors: dict[str, str] = {}

        if not is_valid_cron_expression(data["cron_expression"]):
            errors["cron_expression"] = "Invalid cron expression."

        if len(errors) > 0:
            raise FormValidationError(errors)
        return await super().validate(request, data)
