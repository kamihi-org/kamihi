"""
Job view module for Kamihi web application.

License:
    MIT

"""

from collections.abc import Callable
from typing import Any

from starlette.requests import Request
from starlette_admin import StringField, row_action
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
        "per_user",
        StringField(
            "cron_expression",
            help_text="Cron expression for scheduling the job. E.g., '*/5 * * * *' for every 5 minutes. "
            "You can use https://crontab.guru/ to help generate valid expressions.",
        ),
        "args",
    ]
    run_job_callback: Callable

    def __init__(self, *args, run_job_callback: Callable, **kwargs) -> None:  # noqa: ANN002, ANN003
        """
        Initialize the JobView with optional run_job_callback.

        Args:
            *args: Positional arguments.
            run_job_callback (list): A list of callables to run when a job is executed.
            **kwargs: Keyword arguments.

        """
        super().__init__(*args, **kwargs)
        self.run_job_callback = run_job_callback

    async def validate(self, request: Request, data: dict[str, Any]) -> None:
        """Validate the job data before creating or editing."""
        errors: dict[str, str] = {}

        if not is_valid_cron_expression(data["cron_expression"]):
            errors["cron_expression"] = "Invalid cron expression."

        if len(errors) > 0:
            raise FormValidationError(errors)
        return await super().validate(request, data)

    @row_action(
        name="run_job",
        text="Run job manually",
        icon_class="fas fa-play",
        confirmation="Are you sure you want to run this job manually?",
        submit_btn_text="Yes, run job",
        submit_btn_class="btn-success",
    )
    async def run_job(self, request: Request, pk: Any) -> str:
        """Run the job manually."""
        await self.run_job_callback(pk)
        return "Job executed successfully."
