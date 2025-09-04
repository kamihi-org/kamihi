"""
User management module for Kamihi CLI.

License:
    MIT

"""

import json
from typing import Annotated

import typer
from loguru import logger
from mongoengine import FieldDoesNotExist, ValidationError
from sqlmodel import Session, select

from kamihi.base.config import KamihiSettings
from kamihi.base.logging import configure_logging
from kamihi.cli.commands.run import import_models
from kamihi.db import User, get_engine

app = typer.Typer()


def telegram_id_callback(value: int) -> int:
    """
    Validate the Telegram ID.

    Args:
        value (int): The Telegram ID to validate.

    Returns:
        int: The validated Telegram ID.

    Raises:
        typer.BadParameter: If the Telegram ID is invalid.

    """
    if not isinstance(value, int) or value <= 0 or len(str(value)) > 16:
        msg = "Must be a positive integer with up to 16 digits."
        raise typer.BadParameter(msg)
    return value


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
) -> None:
    """Add a new user."""
    settings = KamihiSettings.from_yaml(ctx.obj.config) if ctx.obj.config else KamihiSettings()
    settings.log.file_enable = False
    settings.log.notification_enable = False
    configure_logging(logger, settings.log)

    user_data: dict = {"telegram_id": telegram_id, "is_admin": is_admin}

    lg = logger.bind(**user_data)

    import_models(ctx.obj.cwd / "models")

    with lg.catch(ValidationError, message="User inputted is not valid.", onerror=onerror):
        with Session(get_engine()) as session:
            statement = select(User).where(User.telegram_id == telegram_id)
            existing_user = session.exec(statement).first()
            if existing_user:
                lg.error("User with Telegram ID {telegram_id} already exists.", telegram_id=telegram_id)
                raise typer.Exit(1)
            user = User(**user_data)
            session.add(user)
            session.commit()

    lg.success("User added.")
