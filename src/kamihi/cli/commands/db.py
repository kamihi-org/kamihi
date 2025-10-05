"""
Database management module for Kamihi CLI.

License:
    MIT

"""

import contextlib
from typing import Annotated

import typer
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from loguru import logger

from kamihi.base import get_settings
from kamihi.base.logging import StreamToLogger
from kamihi.cli.utils import import_models

app = typer.Typer()


def revision_callback(ctx: typer.Context, value: str) -> str:
    """
    Ensure the revision value is valid.

    Args:
        ctx (typer.Context): The Typer context.
        value (str): The revision value.

    Returns:
        str: The validated revision value.

    """
    if not value or not isinstance(value, str):
        raise typer.BadParameter("Invalid revision value")
    script = ScriptDirectory.from_config(ctx.obj.alembic_cfg)
    value = script.as_revision_number(value)
    if value is None:
        raise typer.BadParameter("Revision not found")
    return value


@app.callback()
def main(ctx: typer.Context) -> None:
    """Database management commands for Kamihi CLI."""
    settings = get_settings()

    import_models(ctx.obj.cwd / "models")

    ctx.obj.alembic_cfg = Config(toml_file=ctx.obj.cwd / "pyproject.toml")
    ctx.obj.alembic_cfg.set_main_option("sqlalchemy.url", settings.db.url)

    if not (ctx.obj.cwd / "migrations").exists():
        logger.error("No migrations directory found. Please run 'kamihi init' first.")
        raise typer.Exit(code=1)


@app.command("migrate")
def migrate(ctx: typer.Context) -> None:
    """Run database migrations."""
    with contextlib.redirect_stdout(StreamToLogger(logger, "DEBUG")):
        res = command.revision(ctx.obj.alembic_cfg, autogenerate=True, message="auto migration")
    logger.bind(revision=res.revision).success("Migrated")


@app.command("upgrade")
def upgrade(
    ctx: typer.Context,
    revision: Annotated[
        str,
        typer.Option(
            "--revision", "-r", help="The revision to upgrade to.", show_default="head", callback=revision_callback
        ),
    ] = "head",
) -> None:
    """Upgrade the database to a later version."""
    command.upgrade(ctx.obj.alembic_cfg, revision)
    logger.bind(revision=revision).success("Upgraded")


@app.command("downgrade")
def downgrade(
    ctx: typer.Context,
    revision: Annotated[
        str,
        typer.Option(
            "--revision", "-r", help="The revision to downgrade to.", show_default="-1", callback=revision_callback
        ),
    ] = "-1",
) -> None:
    """Downgrade the database to an earlier version."""
    command.downgrade(ctx.obj.alembic_cfg, revision)
    logger.bind(revision=revision).success("Downgraded")
