"""
Functional tests for the action decorator.

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
                async def start():
                    return "test"
            """,
        }
    ],
)
async def test_action_decorator_no_parentheses(user_in_db, add_permission_for_user, chat: Conversation, actions_folder):
    """Test the action decorator without parentheses."""
    add_permission_for_user(user_in_db, "start")

    await chat.send_message("/start")
    response = await chat.get_response()

    assert response.text == "test"


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
                async def start():
                    return "Hello! I'm your friendly bot. How can I help you today?"
            """,
            "start2/__init__.py": "",
            "start2/start2.py": """\
                from kamihi import bot
                
                @bot.action
                async def start2():
                    return "Hello! I'm not your friendly bot."
            """,
        }
    ],
)
async def test_action_multiple_defined(user_in_db, add_permission_for_user, chat: Conversation, actions_folder):
    """Test the action decorator with multiple defined actions."""
    add_permission_for_user(user_in_db, "start")
    add_permission_for_user(user_in_db, "start2")

    await chat.send_message("/start")
    response = await chat.get_response()

    assert response.text == "Hello! I'm your friendly bot. How can I help you today?"

    await chat.send_message("/start2")
    response = await chat.get_response()

    assert response.text == "Hello! I'm not your friendly bot."
