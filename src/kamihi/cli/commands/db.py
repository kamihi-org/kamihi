"""
Database management module for Kamihi CLI.

License:
    MIT

"""
from pathlib import Path
from typing import Annotated

from alembic import command
from alembic.config import Config
import typer
from loguru import logger

from kamihi import KamihiSettings, configure_logging
from kamihi.cli.utils import import_models

app = typer.Typer()


@app.callback()
def main(ctx: typer.Context) -> None:
    """
    Database management commands for Kamihi CLI.
    """
    ctx.obj.settings = KamihiSettings.from_yaml(ctx.obj.config) if ctx.obj.config is not None else KamihiSettings()

    configure_logging(logger, ctx.obj.settings.log)

    import_models(ctx.obj.cwd / "models")

    ctx.obj.config_path = ctx.obj.cwd / "alembic.ini"
    ctx.obj.toml_path = ctx.obj.cwd / "pyproject.toml"
    ctx.obj.migrations_path = ctx.obj.cwd / "migrations"

    ctx.obj.alembic_cfg = Config(toml_file=ctx.obj.toml_path)
    ctx.obj.alembic_cfg.set_main_option("sqlalchemy.url", ctx.obj.settings.db.url)

    if not (ctx.obj.cwd / "migrations").exists():
        logger.error("No migrations directory found. Please run 'kamihi init' first.")
        raise typer.Exit(code=1)


@app.command("migrate")
def migrate(ctx: typer.Context) -> None:
    """Run database migrations."""
    command.revision(ctx.obj.alembic_cfg, autogenerate=True, message="auto migration")
    logger.info("Migration created.")


@app.command("upgrade")
def upgrade(
        ctx: typer.Context,
        revision: Annotated[
            str,
            typer.Option(
                "--revision", "-r", help="The revision to upgrade to.", show_default="head"
            )
        ] = "head"
) -> None:
    """Upgrade the database to a later version."""
    command.upgrade(ctx.obj.alembic_cfg, revision)
    logger.info(f"Database upgraded to revision {revision}.")


@app.command("downgrade")
def downgrade(
        ctx: typer.Context,
        revision: Annotated[
            str,
            typer.Option(
                "--revision", "-r", help="The revision to downgrade to.", show_default="-1"
            )
        ] = "-1"
) -> None:
    """Downgrade the database to an earlier version."""
    command.downgrade(ctx.obj.alembic_cfg, revision)
    logger.info(f"Database downgraded to revision {revision}.")
