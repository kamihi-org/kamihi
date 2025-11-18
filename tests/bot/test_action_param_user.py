"""
Test the `user` parameter in action function signatures.

License:
    MIT

"""

import pytest
from telethon.tl.custom import Conversation


@pytest.mark.asyncio
@pytest.mark.usefixtures("kamihi")
@pytest.mark.parametrize(
    "actions_folder",
    [
        {
            "start/__init__.py": "",
            "start/start.py": """\
                from kamihi import bot
                             
                @bot.action
                async def start(user):
                    return f"Hello, user with ID {user.telegram_id}!"
            """,
        }
    ],
)
async def test_user(user, add_permission_for_user, chat: Conversation, actions_folder):
    """Test the action decorator without parentheses."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response = await chat.get_response()

    assert response.text == f"Hello, user with ID {user['telegram_id']}!"


@pytest.mark.asyncio
@pytest.mark.usefixtures("kamihi")
@pytest.mark.parametrize(
    "actions_folder",
    [
        {
            "start/__init__.py": "",
            "start/start.py": """\
                from kamihi import bot
                             
                @bot.action
                async def start(user):
                    return f"Hello, {user.name}!"
            """,
        }
    ],
)
@pytest.mark.parametrize(
    "models_folder",
    [
        {
            "user.py": """\
                from kamihi.db import BaseUser
                from sqlalchemy import Column, String
                
                class User(BaseUser):
                    __table_args__ = {'extend_existing': True}
                    name = Column(String, nullable=True)
            """,
        }
    ],
)
@pytest.mark.parametrize("user_custom_data", [{"name": "John Doe"}])
async def test_custom_user(
    user,
    add_permission_for_user,
    chat: Conversation,
    actions_folder,
    models_folder,
    user_custom_data,
):
    """Test the action decorator without parentheses."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response = await chat.get_response()

    assert response.text == f"Hello, {user['name']}!"
