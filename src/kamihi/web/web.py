"""
TODO: one-line module description.

TODO: Additional details about the module, its purpose, and any necessary
background information. Explain what functions or classes are included.

License:
    MIT

Examples:
    [Examples of how to use the module/classes/functions]

Attributes:
    [List any relevant module-level attributes with types and descriptions]

"""

from pathlib import Path
from threading import Thread

from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from loguru import logger
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer

from kamihi.base.config import KamihiSettings
from kamihi.db.models import Base

FLASK_PATH = Path(__file__).parent
PROJECT_PATH = Path.cwd()


class KamihiWeb(Thread):
    """
    KamihiWeb is a class that sets up a web server for the Kamihi application.

    This class is responsible for creating and running a Flask web server
    with an admin interface using Flask-Admin. It also handles the database
    connection and configuration.

    Attributes:
        bot_settings (KamihiSettings): The settings for the Kamihi bot.
        db (Database): The database connection for the Kamihi bot.
        flask_app (Flask): The Flask application instance.
        admin (Admin): The Flask-Admin instance for the admin interface.

    """

    def __init__(self, settings: KamihiSettings) -> None:
        """Initialize the KamihiWeb instance."""
        super().__init__()
        self.bot_settings = settings
        self.daemon = True

        self.flask_app = None
        self.admin = None
        self.db = None

    def model_views(self) -> list[ModelView]:
        """Return model views for models inputted."""
        return [ModelView(model, self.db.session) for model in Base.__subclasses__()]

    def _create_app(self) -> None:
        self.flask_app = Flask(
            "kamihi",
            template_folder=FLASK_PATH / "templates",
            static_folder=FLASK_PATH / "static",
        )

        if self.bot_settings.db_url.startswith("sqlite:///"):
            self.flask_app.config["SQLALCHEMY_DATABASE_URI"] = self.bot_settings.db_url.replace(
                "sqlite:///", "sqlite:///" + str(PROJECT_PATH) + "/"
            )
        else:
            self.flask_app.config["SQLALCHEMY_DATABASE_URI"] = self.bot_settings.db_url

        self.flask_app.config["SECRET_KEY"] = self.bot_settings.web.secret
        self.flask_app.config.from_prefixed_env("KAMIHI_FLASK__")

        self.db = SQLAlchemy(model_class=Base)
        self.db.init_app(self.flask_app)

        self.admin = Admin(self.flask_app, name="kamihi")
        self.admin.add_views(*self.model_views())

    def run(self) -> None:
        """Run the Flask webapp."""
        self._create_app()
        http_server = HTTPServer(WSGIContainer(self.flask_app))
        http_server.listen(self.bot_settings.web.port, address=self.bot_settings.web.host)
        IOLoop.instance().call_later(
            0,
            lambda: logger.info(
                "Admin interface started on http://{host}:{port}/admin",
                host=self.bot_settings.web.host,
                port=self.bot_settings.web.port,
            ),
        )
        IOLoop.instance().start()
