"""
User management module for Kamihi CLI.

License:
    MIT

"""

import json
from typing import Annotated

import typer
from loguru import logger

from kamihi import KamihiSettings, _init_bot
from kamihi.cli.commands.run import import_models
from kamihi.users import get_user_from_telegram_id
from kamihi.users.models import User

app = typer.Typer()


def parse_json(data: str) -> dict:
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


@app.command()
def add(
    ctx: typer.Context,
    telegram_id: Annotated[int, typer.Argument(..., help="Telegram ID of the user")],
    is_admin: Annotated[bool, typer.Option("--admin", "-a", help="Is the user an admin?")] = False,  # noqa: FBT002
    data: Annotated[
        str | None,
        typer.Option(
            "--data",
            "-d",
            help="Additional data for the user in JSON format. For use with custom user classes.",
            show_default=False,
            callback=parse_json,
        ),
    ] = None,
) -> None:
    """Add a new user."""
    settings = KamihiSettings.from_yaml(ctx.obj.config) if ctx.obj.config else KamihiSettings()
    settings.log.file_enable = False
    settings.log.notification_enable = False
    _init_bot(settings)
    lg = logger.bind(
        telegram_id=telegram_id,
        is_admin=is_admin,
        **data or {},
    )

    import_models(ctx.obj.cwd / "models")

    if User.get_model() == User:
        lg.warning("No custom user model found. Using default User model and ignoring extra data provided.")
        data = {}
        lg = logger.bind(
            telegram_id=telegram_id,
            is_admin=is_admin,
        )

    if get_user_from_telegram_id(telegram_id):
        lg.error("User with this Telegram ID already exists.")
        raise typer.Exit(1)

    user = User.get_model()(telegram_id=telegram_id, is_admin=is_admin, **data)
    user.save()

    lg.bind(telegram_id=telegram_id, is_admin=is_admin, **data).info("User added successfully.")
