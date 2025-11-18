"""
Test cases for bot actions that return strings.

License:
    MIT

"""

import pytest
from telethon.tl.custom import Conversation, Message


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
                    return "Hello!"
            """,
        },
        {
            "start/__init__.py": "",
            "start/start.py": """\
                from kamihi import bot
                             
                @bot.action
                async def start() -> str:
                    return "Hello!"
            """,
        },
    ],
    ids=["not_annotated", "annotated"],
)
async def test_string(user, add_permission_for_user, chat: Conversation, actions_folder):
    """Test actions that return a string."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response: Message = await chat.get_response()

    assert response.text == "Hello!"
