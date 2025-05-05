"""
Web interface main file.

License:
    MIT

"""

import inspect
import logging
from pathlib import Path
from threading import Thread

import uvicorn
from loguru import logger
from sqlalchemy import Engine
from starlette.applications import Starlette
from starlette_admin import CustomView
from starlette_admin.contrib.sqlmodel import Admin, ModelView

from kamihi.base.config import KamihiSettings
from kamihi.db.models import User

WEB_PATH = Path(__file__).parent


class _InterceptHandler(logging.Handler):  # skipcq: PY-A6006
    def emit(self, record: logging.LogRecord) -> None:
        frame, depth = inspect.currentframe(), 0
        while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
            frame = frame.f_back
            depth += 1

        level = logger.level("TRACE").name if record.name == "uvicorn.access" else logger.level(record.levelname).name

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class KamihiWeb(Thread):
    """
    KamihiWeb is a class that sets up a web server for the Kamihi application.

    This class is responsible for creating and running a web server
    with an admin interface. It also handles the database
    connection and configuration.

    Attributes:
        bot_settings (KamihiSettings): The settings for the Kamihi bot.
        db (Database): The database connection for the Kamihi bot.
        app (Starlette): The application instance.
        admin (Admin): The Starlette-Admin instance for the admin interface.

    """

    bot_settings: KamihiSettings
    db: Engine
    app: Starlette | None
    admin: Admin | None

    def __init__(self, settings: KamihiSettings, engine: Engine) -> None:
        """Initialize the KamihiWeb instance."""
        super().__init__()
        self.bot_settings = settings
        self.daemon = True
        self.engine = engine

        self.app = None
        self.admin = None

    def _create_app(self) -> None:
        self.app = Starlette()

        admin = Admin(
            self.engine,
            title="Kamihi",
            base_url="/",
            templates_dir=str(WEB_PATH / "templates"),
            statics_dir=str(WEB_PATH / "static"),
            index_view=CustomView(label="Home", icon="fa fa-home", path="/", template_path="home.html"),
            favicon_url="/statics/images/favicon.ico",
        )
        admin.add_view(ModelView(User, icon="fas fa-user"))

        admin.mount_to(self.app)

    def run(self) -> None:
        """Run the app."""
        self._create_app()

        uvicorn.run(
            self.app,
            host=self.bot_settings.web.host,
            port=self.bot_settings.web.port,
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
