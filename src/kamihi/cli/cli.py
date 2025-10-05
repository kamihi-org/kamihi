"""
Main file of the CLI utility for the Kamihi framework.

License:
    MIT

"""

from pathlib import Path
from typing import Annotated

import typer
from loguru import logger

from .commands import action_app, db_app, init_app, permission_app, role_app, run_app, user_app, version_app

app = typer.Typer()
app.add_typer(version_app)
app.add_typer(init_app)
app.add_typer(action_app, name="action")
app.add_typer(run_app)
app.add_typer(user_app, name="user")
app.add_typer(db_app, name="db")
app.add_typer(permission_app, name="permission")
app.add_typer(role_app, name="role")


class Context:
    """
    Context for the Kamihi CLI utility.

    This class holds the context data for the CLI commands.
    """

    def __init__(self) -> None:
        """Initialize the context with default values."""
        self.cwd: Path = Path.cwd()
        self.templates: Path = Path(__file__).parent / "templates"
        self.project: Path = self.cwd
        self.config: Path = self.project / "kamihi.yaml"


@app.callback()
def main(
    ctx: typer.Context,
    settings_path: Annotated[
        Path | None,
        typer.Option(
            ...,
            help="Path to the Kamihi settings file",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
            show_default="kamihi.yaml",
        ),
    ] = None,
) -> None:
    """
    Kamihi CLI utility.

    This utility provides commands to manage and interact with the Kamihi framework.
    """
    ctx.obj = Context()

    if ctx.invoked_subcommand not in ["init", "version"]:
        from kamihi.base import init_settings

        init_settings(settings_path)

        from kamihi.base import configure_logging

        configure_logging(logger)
        logger.bind(settings_file=str(settings_path)).debug("Configured logging and loaded settings")

    if ctx.invoked_subcommand in ["permission", "role", "run", "user"]:
        from kamihi.cli.utils import import_models
        from kamihi.db import init_engine

        import_models(ctx.obj.cwd / "models")
        logger.bind(folder=str(ctx.obj.cwd / "models")).debug("Imported models")

        init_engine()
        logger.debug("Initialized database engine")


if __name__ == "__main__":
    app()
