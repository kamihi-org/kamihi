"""
Role management commands for Kamihi CLI.

License:
    MIT

"""

from typing import Annotated

import typer
from loguru import logger
from sqlalchemy import select
from sqlalchemy.orm import Session

from kamihi.cli.utils import telegram_id_callback
from kamihi.db import BaseUser, Role, get_engine

app = typer.Typer()


@app.command()
def add(
    name: Annotated[str, typer.Argument(..., help="Name of the role to add.")],
) -> None:
    """Add a new role and optionally assign it to specified users."""
    lg = logger.bind(name=name)

    with Session(get_engine()) as session:
        role = session.execute(select(Role).where(Role.name == name)).scalar_one_or_none()
        if role:
            lg.error("Role already exists")
            raise typer.Exit(1)

        role = Role(name=name)
        session.add(role)
        session.commit()
        lg.success("Role added")


@app.command()
def assign(
    role: Annotated[str, typer.Argument(..., help="Name of the role to assign to users.")],
    users: Annotated[
        list[int],
        typer.Argument(..., help="Telegram ID of the user(s) to assign the role to.", callback=telegram_id_callback),
    ],
) -> None:
    """Assign an existing role to specified users."""
    lg = logger.bind(role=role)

    with Session(get_engine()) as session:
        role_obj = session.execute(select(Role).where(Role.name == role)).scalar_one_or_none()
        if not role_obj:
            lg.error("Role does not exist")
            raise typer.Exit(1)

        assigned_users = []
        for telegram_id in users:
            lg2 = lg.bind(telegram_id=telegram_id)
            user = session.execute(
                select(BaseUser.cls()).where(BaseUser.cls().telegram_id == telegram_id)
            ).scalar_one_or_none()
            if not user:
                lg2.warning("User not found, skipping...")
                continue

            if role_obj in user.roles:
                lg2.warning("User already has role, skipping...")
                continue

            user.roles.append(role_obj)
            assigned_users.append(telegram_id)
            lg2.debug("Role assigned to user")

        session.commit()
        lg.success("Role assigned to users", users=assigned_users)
