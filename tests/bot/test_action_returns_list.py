"""
Test cases for bot actions that return lists of other types.

License:
    MIT

"""

import pytest
from telethon.tl.custom import Conversation, Message

from tests.utils.media import random_image


@pytest.mark.asyncio
@pytest.mark.usefixtures("kamihi")
@pytest.mark.parametrize(
    "actions_folder,messages",
    [
        (
            {
                "start/__init__.py": "",
                "start/start.py": """\
                    from kamihi import bot
                                 
                    @bot.action
                    async def start() -> list[str]:
                        return ["I now", "can send", "many messages", "!!"]
                """,
            },
            ["I now", "can send", "many messages", "!!"],
        ),
        (
            {
                "start/__init__.py": "",
                "start/start.py": """\
                    from pathlib import Path
                    from kamihi import bot
                
                    @bot.action
                    async def start() -> list[str | bot.Photo]:
                        return ["This is a message", bot.Photo(Path("actions/start/image.jpg"), caption="and this is a photo!")]
                """,
                "start/image.jpg": random_image(),
            },
            ["This is a message", "and this is a photo!"],
        ),
    ],
)
async def test_list(user, add_permission_for_user, chat: Conversation, actions_folder, messages):
    """Test actions that return multiple messages."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")

    for message in messages:
        response: Message = await chat.get_response()
        assert response.text == message
