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

from kamihi import KamihiSettings, _init_bot
from kamihi.cli.commands.run import import_models
from kamihi.users.models import User

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
    _init_bot(settings)

    user_data = data or {}
    user_data["telegram_id"] = telegram_id
    user_data["is_admin"] = is_admin

    lg = logger.bind(**user_data)

    import_models(ctx.obj.cwd / "models")

    if User.get_model() == User and data:
        lg.warning("No custom user model found, ignoring extra data provided.")
        user_data = {"telegram_id": telegram_id, "is_admin": is_admin}

    with lg.catch(FieldDoesNotExist, message="Custom user model does not have the field provided.", onerror=onerror):
        user = User.get_model()(**user_data)
    with lg.catch(ValidationError, message="User inputted is not valid.", onerror=onerror):
        user.validate()
        user.save()

    lg.success("User added.")
