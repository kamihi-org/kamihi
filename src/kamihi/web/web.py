"""
Web interface main file.

License:
    MIT

"""

import inspect
import logging
from collections.abc import Callable
from pathlib import Path
from threading import Thread
from typing import Literal

import uvicorn
from loguru import logger
from starlette.applications import Starlette
from starlette_admin import CustomView
from starlette_admin.contrib.sqla import Admin
from starlette_admin.views import Link

from kamihi.base import get_settings
from kamihi.db import BaseUser, Job, Permission, RegisteredAction, Role, get_engine

from .views import ActionView, BaseView, JobView, UserView

WEB_PATH = Path(__file__).parent


class _InterceptHandler(logging.Handler):  # skipcq: PY-A6006
    def emit(self, record: logging.LogRecord) -> None:
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        level = logger.level("TRACE").name

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class KamihiWeb(Thread):
    """
    KamihiWeb is a class that sets up a web server for the Kamihi application.

    This class is responsible for creating and running a web server
    with an admin interface. It also handles the database
    connection and configuration.

    Attributes:
        app (Starlette): The application instance.
        admin (Admin): The Starlette-Admin instance for the admin interface.

    """

    hooks: dict[
        Literal[
            "before_create", "after_create", "before_edit", "after_edit", "before_delete", "after_delete", "run_job"
        ],
        list[Callable],
    ]

    app: Starlette | None
    admin: Admin | None
    host: str
    port: int

    def __init__(
        self,
        hooks: dict[
            Literal[
                "before_create", "after_create", "before_edit", "after_edit", "before_delete", "after_delete", "run_job"
            ],
            list[Callable],
        ] = None,
    ) -> None:
        """Initialize the KamihiWeb instance."""
        settings = get_settings()

        super().__init__()

        self.hooks = hooks
        self.host = settings.web.host
        self.port = settings.web.port

        self.daemon = True

        self.app = None
        self.admin = None

    def _create_app(self) -> None:
        self.app = Starlette(
            on_startup=[
                lambda: logger.success(
                    "Admin interface started on http://{host}:{port}",
                    host=self.host,
                    port=self.port,
                ),
            ],
        )

        admin = Admin(
            get_engine(),
            title="Kamihi",
            base_url="/",
            templates_dir=str(WEB_PATH / "templates"),
            statics_dir=str(WEB_PATH / "static"),
            index_view=CustomView(label="Home", icon="fa fa-home", path="/", template_path="home.html"),
            favicon_url="/statics/images/favicon.ico",
        )

        admin.add_view(ActionView(RegisteredAction, label="Actions", icon="fas fa-circle-play", hooks=self.hooks))
        admin.add_view(UserView(BaseUser.cls(), label="Users", icon="fas fa-user", hooks=self.hooks))
        admin.add_view(BaseView(Role, icon="fas fa-tags", hooks=self.hooks))
        admin.add_view(BaseView(Permission, icon="fas fa-check", hooks=self.hooks))
        if get_settings().jobs.enabled:
            admin.add_view(
                JobView(Job, icon="fas fa-clock", hooks=self.hooks, run_job_callback=self.hooks.get("run_job")[0])
            )
        admin.add_view(
            Link(label="Documentation", icon="fa fa-book", url="https://kamihi-org.github.io/kamihi/", target="_blank")
        )

        admin.mount_to(self.app)

    def run(self) -> None:
        """Run the app."""
        self._create_app()

        uvicorn.run(
            self.app,
            host=self.host,
            port=self.port,
            log_config={
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "default": {
                        "()": "uvicorn.logging.DefaultFormatter",
                        "fmt": "%(message)s",
                    },
                    "access": {
                        "()": "uvicorn.logging.AccessFormatter",
                        "fmt": '%(client_addr)s - "%(request_line)s" %(status_code)s',  # noqa: E501
                    },
                },
                "handlers": {
                    "default": {
                        "formatter": "default",
                        "class": "kamihi.web.web._InterceptHandler",
                    },
                    "access": {
                        "formatter": "access",
                        "class": "kamihi.web.web._InterceptHandler",
                    },
                },
                "loggers": {
                    "uvicorn": {"handlers": ["default"], "level": "DEBUG", "propagate": False},
                    "uvicorn.error": {"level": "DEBUG"},
                    "uvicorn.access": {"handlers": ["access"], "level": "DEBUG", "propagate": False},
                },
            },
        )
