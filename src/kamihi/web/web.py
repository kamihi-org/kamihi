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
from flask_admin.contrib.peewee import ModelView
from loguru import logger
from peewee import Database
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.wsgi import WSGIContainer

from kamihi.base.config import KamihiSettings
from kamihi.db.models import BaseModel


class KamihiWeb(Thread):
    """
    KamihiWeb is a class that sets up a web server for the Kamihi application.

    This class is responsible for creating and running a Flask web server
    with an admin interface using Flask-Admin. It also handles the database
    connection and configuration.

    Attributes:
        bot_settings (KamihiSettings): The settings for the Kamihi bot.
        database (Database): The database connection for the Kamihi bot.
        models (list[type[BaseModel]]): A list of models to be displayed in the admin interface.
        flask_app (Flask): The Flask application instance.
        admin (Admin): The Flask-Admin instance for the admin interface.

    """

    def __init__(self, settings: KamihiSettings, database: Database, models_to_show: list[type[BaseModel]]) -> None:
        """Initialize the KamihiWeb instance."""
        super().__init__()
        self.bot_settings = settings
        self.database = database
        self.models = models_to_show
        self.daemon = True

        self.flask_app = None
        self.admin = None

    @property
    def model_views(self) -> list[ModelView]:
        """Return model views for models inputted."""
        return [ModelView(model, model.__name__.capitalize()) for model in self.models]

    def _create_app(self) -> None:
        self.flask_app = Flask(
            "kamihi",
            template_folder=Path(__file__).parent / "templates",
            static_folder=Path(__file__).parent / "static",
        )

        self.flask_app.config["DATABASE"] = self.bot_settings.db_url
        self.flask_app.config["SECRET_KEY"] = self.bot_settings.web.secret
        self.flask_app.config["HOST"] = self.bot_settings.web.host
        self.flask_app.config["PORT"] = self.bot_settings.web.port
        self.flask_app.config.from_prefixed_env("KAMIHI_FLASK__")

        self.admin = Admin(self.flask_app, name="kamihi", template_mode="bootstrap3")
        self.admin.add_views(*self.model_views)

    def run(self) -> None:
        """Run the Flask webapp."""
        self._create_app()
        http_server = HTTPServer(WSGIContainer(self.flask_app))
        http_server.listen(5000)
        IOLoop.instance().call_later(
            0,
            lambda: logger.info(
                "Admin interface started on http://{host}:{port}/admin",
                host=self.bot_settings.web.host,
                port=self.bot_settings.web.port,
            ),
        )
        IOLoop.instance().start()
