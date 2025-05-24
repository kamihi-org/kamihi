"""
Functional tests for action parameter injections.

License:
    MIT

"""

from textwrap import dedent

import pytest
from mongoengine import StringField
from pytest_docker_tools.wrappers import Container
from telethon.tl.custom import Conversation


@pytest.mark.asyncio
@pytest.mark.usefixtures("kamihi")
@pytest.mark.parametrize(
    "actions_folder",
    [
        {
            "actions/start/__init__.py": "".encode(),
            "actions/start/start.py": dedent("""\
            from kamihi import bot
                         
            @bot.action
            async def start(user):
                return f"Hello, user with ID {user.telegram_id}!"
        """).encode(),
        }
    ],
)
async def test_action_parameter_user(user_in_db, add_permission_for_user, chat: Conversation, actions_folder):
    """Test the action decorator without parentheses."""
    add_permission_for_user(user_in_db, "start")

    await chat.send_message("/start")
    response = await chat.get_response()

    assert response.text == f"Hello, user with ID {user_in_db['telegram_id']}!"


@pytest.mark.asyncio
@pytest.mark.usefixtures("kamihi")
@pytest.mark.parametrize(
    "actions_folder",
    [
        {
            "actions/start/__init__.py": "".encode(),
            "actions/start/start.py": dedent("""\
            from kamihi import bot
                         
            @bot.action
            async def start(user):
                return f"Hello, {user.name}!"
        """).encode(),
        }
    ],
)
@pytest.mark.parametrize(
    "models_folder",
    [
        {
            "models/user.py": dedent("""\
                from kamihi import bot, BaseUser
                from mongoengine import StringField
                 
                @bot.user_class
                class MyCustomUser(BaseUser):
                    name: str = StringField()
            """).encode(),
        }
    ],
)
@pytest.mark.parametrize("user_custom_data", [{"name": "John Doe"}])
async def test_action_parameter_user_custom(
    user_in_db,
    add_permission_for_user,
    chat: Conversation,
    actions_folder,
    models_folder,
    user_custom_data,
):
    """Test the action decorator without parentheses."""
    add_permission_for_user(user_in_db, "start")

    await chat.send_message("/start")
    response = await chat.get_response()

    assert response.text == f"Hello, {user_in_db['name']}!"
