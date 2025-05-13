"""
Web interface main file.

License:
    MIT

"""

import inspect
import logging
from pathlib import Path
from threading import Thread
from typing import Literal

import uvicorn
from loguru import logger
from starlette.applications import Starlette
from starlette_admin import CustomView
from starlette_admin.contrib.mongoengine import Admin

from kamihi.base.config import DatabaseSettings, WebSettings
from kamihi.bot.models import RegisteredAction
from kamihi.db.mongo import connect, disconnect
from kamihi.users.models import Permission, Role, User

from .views import HooksView, ReadOnlyView

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
        settings (WebSettings): The settings for the Kamihi bot.
        db_settings (DatabaseSettings): The database settings for the Kamihi bot.
        app (Starlette): The application instance.
        admin (Admin): The Starlette-Admin instance for the admin interface.

    """

    settings: WebSettings
    db_settings: DatabaseSettings
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

    app: Starlette | None
    admin: Admin | None

    def __init__(
        self,
        settings: WebSettings,
        db_settings: DatabaseSettings,
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
        ] = None,
    ) -> None:
        """Initialize the KamihiWeb instance."""
        super().__init__()
        self.settings = settings
        self.db_settings = db_settings
        self.hooks = hooks

        self.daemon = True

        self.app = None
        self.admin = None

    def _create_app(self) -> None:
        self.app = Starlette(
            on_startup=[
                lambda: connect(self.db_settings),
                lambda: logger.info(
                    "Web server started on http://{host}:{port}",
                    host=self.settings.host,
                    port=self.settings.port,
                ),
            ],
            on_shutdown=[disconnect],
        )

        admin = Admin(
            title="Kamihi",
            base_url="/",
            templates_dir=str(WEB_PATH / "templates"),
            statics_dir=str(WEB_PATH / "static"),
            index_view=CustomView(label="Home", icon="fa fa-home", path="/", template_path="home.html"),
            favicon_url="/statics/images/favicon.ico",
        )

        admin.add_view(HooksView(User.get_model(), icon="fas fa-user", hooks=self.hooks))
        admin.add_view(HooksView(Role, icon="fas fa-tags", hooks=self.hooks))
        admin.add_view(ReadOnlyView(RegisteredAction, name="Actions", icon="fas fa-circle-play", hooks=self.hooks))
        admin.add_view(HooksView(Permission, icon="fas fa-check", hooks=self.hooks))

        admin.mount_to(self.app)

    def run(self) -> None:
        """Run the app."""
        self._create_app()

        uvicorn.run(
            self.app,
            host=self.settings.host,
            port=self.settings.port,
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
