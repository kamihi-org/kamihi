"""
Telegram client module.

This module provides a Telegram client for sending messages and handling commands.

License:
    MIT

"""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from typing import Any

from apscheduler.triggers.cron import CronTrigger
from loguru import logger
from sqlalchemy.orm import Session
from telegram import BotCommand, BotCommandScopeChat, Update
from telegram.constants import ParseMode
from telegram.error import TelegramError
from telegram.ext import (
    Application,
    ApplicationBuilder,
    BaseHandler,
    CallbackContext,
    CallbackQueryHandler,
    Defaults,
    MessageHandler,
    filters,
)

from kamihi.base import get_settings
from kamihi.base.utils import UUID4_REGEX
from kamihi.datasources import DataSource
from kamihi.db import Job, get_engine

from .default_handlers import default, error
from .handlers.page_handler import page_callback


class TelegramClient:
    """
    Telegram client class.

    This class provides methods to send messages and handle commands.

    """

    app: Application
    _base_url: str = "https://api.telegram.org/bot"
    _base_file_url: str = "https://api.telegram.org/file/bot"
    _builder: ApplicationBuilder
    _testing: bool = False

    def __init__(self, _post_init: Callable, _post_shutdown: Callable) -> None:
        """
        Initialize the Telegram client.

        Args:
            _post_init (callable): Function to call after the application is initialized.
            _post_shutdown (callable): Function to call after the application is shut down.

        """
        settings = get_settings()

        if settings.testing:
            self._base_url = "https://api.telegram.org/bot{token}/test"
            self._base_file_url = "https://api.telegram.org/file/bot{token}/test"
            self._testing = True

        # Set up the application with all the settings
        self._builder = Application.builder()
        self._builder.base_url(self._base_url)
        self._builder.base_file_url(self._base_file_url)
        self._builder.token(settings.token)
        self._builder.defaults(
            Defaults(
                tzinfo=settings.timezone_obj,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        )
        self._builder.post_init(_post_init)
        self._builder.post_shutdown(_post_shutdown)

        # Build the application
        self.app: Application = self._builder.build()

    def add_datasources(self, datasources: dict[str, DataSource]) -> None:
        """
        Add data sources to the Telegram client.

        Args:
            datasources (dict[str, DataSource]): Dictionary of data source names and their corresponding callables.

        """
        self.app.bot_data["datasources"] = datasources

    def add_handlers(self, handlers: list[BaseHandler]) -> None:
        """
        Add handlers to the Telegram client.

        Args:
            handlers (list[BaseHandler]): List of handlers to add.

        """
        for handler in handlers:
            with logger.catch(exception=TelegramError, level="ERROR", message="Failed to register handler"):
                self.app.add_handler(handler)

    def add_pages_handler(self) -> None:
        """Add the pages handler to the Telegram client."""
        with logger.catch(exception=TelegramError, level="ERROR", message="Failed to register pages handler"):
            self.app.add_handler(CallbackQueryHandler(page_callback, pattern=rf"^{UUID4_REGEX.pattern}#[0-9]+$"))

    def add_default_handlers(self) -> None:
        """Add default handlers to the Telegram client."""
        settings = get_settings()
        with logger.catch(exception=TelegramError, level="ERROR", message="Failed to register default handlers"):
            if settings.responses.default_enabled:
                self.app.add_handler(MessageHandler(filters.TEXT, default))
            self.app.add_error_handler(error)

    def add_jobs(self, jobs: list[tuple[Job, Callable[[CallbackContext], Coroutine[Any, Any, None]]]]) -> None:
        """Add jobs to the Telegram client."""
        if not get_settings().jobs.enabled:
            logger.debug("Jobs are disabled, skipping job registration")
            return

        logger.trace("Registering jobs...")
        self.app.job_queue.scheduler.remove_all_jobs()
        logger.trace("Removed all existing jobs")
        with Session(get_engine()) as session:
            for job, callback in jobs:
                session.add(job)
                with logger.catch(exception=TelegramError, level="ERROR", message="Failed to register job"):
                    lg = logger.bind(job_id=job.id, action="/" + job.action.name, cron_expression=job.cron_expression)
                    if not job.enabled:
                        lg.info("Disabled, skipping")
                        continue
                    lg.trace("Registering job")
                    self.app.job_queue.run_custom(
                        callback,
                        job_kwargs={
                            "trigger": CronTrigger.from_crontab(job.cron_expression),
                            "replace_existing": True,
                        },
                        data={
                            "args": job.args,
                            "per_user": job.per_user,
                            "users": [user.telegram_id for user in job.effective_users],
                        },
                        name=job.id,
                    )
                    lg.debug("Job registered")
        logger.debug("All jobs registered", jobs=len(jobs))

    async def run_job(self, job_id: str) -> None:
        """
        Run a job by its ID.

        Args:
            job_id (str): The ID of the job to run.

        """
        job = self.app.job_queue.get_jobs_by_name(job_id)
        if not job:
            logger.warning(f"Job with ID {job_id} not found")
            return
        lg = logger.bind(job_id=job_id)
        lg.debug("Running job manually")
        await job[0].run(self.app)
        lg.debug("Job run completed")

    async def reset_scopes(self) -> None:  # noqa: ARG002
        """
        Reset the command scopes for the bot.

        This method clears all command scopes and sets the default commands.
        """
        if self._testing:
            logger.debug("Testing mode, skipping resetting scopes")
            return

        with logger.catch(exception=TelegramError, message="Failed to reset scopes"):
            await self.app.bot.delete_my_commands()
            logger.debug("Scopes erased")

    async def set_scopes(self, scopes: dict[int, list[BotCommand]]) -> None:
        """
        Set the command scopes for the bot.

        Args:
            scopes (dict[int, list[BotCommand]]): The command scopes to set.

        """
        if self._testing:
            logger.debug("Testing mode, skipping setting scopes")
            return

        for user_id, commands in scopes.items():
            lg = logger.bind(user_id=user_id, commands=[command.command for command in commands])
            with lg.catch(
                exception=TelegramError,
                message="Failed to set scopes",
            ):
                await self.app.bot.set_my_commands(
                    commands=commands,
                    scope=BotCommandScopeChat(user_id),
                )
                lg.debug("Scopes set")

    def run(self) -> None:
        """Run the Telegram bot."""
        logger.trace("Starting main loop...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)

    async def stop(self) -> None:
        """Stop the Telegram bot."""
        logger.trace("Stopping main loop...")
        await self.app.stop()
