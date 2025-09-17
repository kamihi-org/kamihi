"""
Permissions management module for Kamihi CLI.

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
from kamihi.db import BaseUser, get_engine, init_engine, RegisteredAction, Role, Permission

app = typer.Typer()


@app.command()
def add(
    ctx: typer.Context,
    action: Annotated[
        str,
        typer.Argument(..., help="Name of the action to assign permission for (without the leading slash)."),
    ],
    users: Annotated[
        list[int],
        typer.Option(
            ...,
            "--user",
            "-u",
            help="Telegram ID of the user(s) to assign the permission to. Can be used multiple times.",
            callback=telegram_id_callback,
        ),
    ],
    roles: Annotated[
        list[str],
        typer.Option(
            ...,
            "--role",
            "-r",
            help="Role name(s) to assign the permission to. Can be used multiple times.",
        ),
    ] = [],
) -> None:
    """Add a new permission for an action to specified users and/or roles."""
    settings = KamihiSettings.from_yaml(ctx.obj.config) if ctx.obj.config else KamihiSettings()
    settings.log.file_enable = False
    settings.log.notification_enable = False
    configure_logging(logger, settings.log)

    import_models(ctx.obj.cwd / "models")
    init_engine(settings.db)

    with Session(get_engine()) as session:
        action_obj = session.execute(
            select(RegisteredAction).where(RegisteredAction.name == action)
        ).scalars().first()
        if not action_obj:
            logger.error(f"Action '/{action}' not found in the database.")
            raise typer.Exit(1)

        users_objs = []
        for user_id in users:
            user = session.execute(
                select(BaseUser.cls()).where(BaseUser.cls().telegram_id == user_id)
            ).scalars().first()
            if not user:
                logger.bind(telegram_id=user_id).error(f"User not found")
                raise typer.Exit(1)
            users_objs.append(user)

        roles_objs = []
        for role_name in roles:
            role = session.execute(
                select(Role).where(Role.name == role_name)
            ).scalars().first()
            if not role:
                logger.bind(name=role_name).error(f"Role not found")
                raise typer.Exit(1)
            roles_objs.append(role)

        permission = Permission(action=action_obj, users=users_objs, roles=roles_objs)
        session.add(permission)
        session.commit()
        logger.info(f"Permission added successfully.")
