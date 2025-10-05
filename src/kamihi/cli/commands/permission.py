"""
Permissions management module for Kamihi CLI.

License:
    MIT

"""

from typing import Annotated

import typer
from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from kamihi.cli.utils import telegram_id_callback
from kamihi.db import BaseUser, Permission, RegisteredAction, Role, get_engine

app = typer.Typer()


@app.command()
def add(
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
    ] = None,
    roles: Annotated[
        list[str],
        typer.Option(
            ...,
            "--role",
            "-r",
            help="Role name(s) to assign the permission to. Can be used multiple times.",
        ),
    ] = None,
) -> None:
    """Add a new permission for an action to specified users and/or roles."""
    if not users and not roles:
        logger.error("At least one user or role must be specified to assign the permission to")
        raise typer.Exit(1)

    with Session(get_engine()) as session:
        action_obj = session.execute(select(RegisteredAction).where(RegisteredAction.name == action)).scalars().first()
        if not action_obj:
            logger.bind(name=action).error("Action not found")
            raise typer.Exit(1)

        users_objs = []
        if users:
            for user_id in users:
                user = (
                    session.execute(select(BaseUser.cls()).where(BaseUser.cls().telegram_id == user_id))
                    .scalars()
                    .first()
                )
                if not user:
                    logger.bind(telegram_id=user_id).error("User not found")
                    raise typer.Exit(1)
                users_objs.append(user)

        roles_objs = []
        if roles:
            for role_name in roles:
                role = session.execute(select(Role).where(Role.name == role_name)).scalars().first()
                if not role:
                    logger.bind(name=role_name).error("Role not found")
                    raise typer.Exit(1)
                roles_objs.append(role)

        permission = Permission(action=action_obj, users=users_objs, roles=roles_objs)
        session.add(permission)
        session.commit()
        logger.bind(
            action=action,
            users=[user.telegram_id for user in users_objs],
            roles=[role.name for role in roles_objs],
        ).success("Permission added")
