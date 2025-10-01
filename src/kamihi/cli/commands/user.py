"""
User management module for Kamihi CLI.

License:
    MIT

"""

import json
from typing import Annotated

import typer
from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from kamihi.base.config import KamihiSettings
from kamihi.base.logging import configure_logging
from kamihi.cli.utils import import_models, telegram_id_callback
from kamihi.db import BaseUser, get_engine, init_engine

app = typer.Typer()


def data_callback(data: str) -> dict:
    """
    Parse a JSON string into a dictionary.

    Args:
        data (str): The JSON string to parse.

    Returns:
        dict: The parsed JSON data.

    Raises:
        typer.BadParameter: If the JSON string is invalid.

    """
    if data:
        try:
            return json.loads(data)
        except json.JSONDecodeError as e:
            msg = f"Invalid JSON data: {e}"
            raise typer.BadParameter(msg) from e
    return {}


def onerror(e: BaseException) -> None:  # noqa: ARG001
    """
    Handle errors during user validation.

    Args:
        e (Exception): The exception raised during validation.

    """
    raise typer.Exit(1)


@app.command()
def add(
    ctx: typer.Context,
    telegram_id: Annotated[int, typer.Argument(..., help="Telegram ID of the user", callback=telegram_id_callback)],
    is_admin: Annotated[bool, typer.Option("--admin", "-a", help="Is the user an admin?")] = False,  # noqa: FBT002
    data: Annotated[
        str | None,
        typer.Option(
            "--data",
            "-d",
            help="Additional data for the user in JSON format. For use with custom user classes.",
            show_default=False,
            callback=data_callback,
        ),
    ] = None,
) -> None:
    """Add a new user."""
    settings = KamihiSettings.from_yaml(ctx.obj.config) if ctx.obj.config else KamihiSettings()
    settings.log.file_enable = False
    settings.log.notification_enable = False
    configure_logging(logger, settings.log)

    user_data = data or {}
    user_data["telegram_id"] = telegram_id
    user_data["is_admin"] = is_admin

    lg = logger.bind(**user_data)

    import_models(ctx.obj.cwd / "models")
    init_engine(settings.db)

    with lg.catch(Exception, message="User inputted is not valid", onerror=onerror), Session(get_engine()) as session:
        statement = select(BaseUser.cls()).where(BaseUser.cls().telegram_id == telegram_id)
        existing_user = session.execute(statement).scalars().first()
        if existing_user:
            lg.error("User already exists")
            raise typer.Exit(1)
        user = BaseUser.cls()(**user_data)
        session.add(user)
        session.commit()

    lg.success("User added")
