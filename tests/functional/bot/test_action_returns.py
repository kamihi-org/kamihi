"""
Functional tests for action returns.

License:
    MIT
"""

from textwrap import dedent

import pytest
from telethon import TelegramClient
from telethon.tl.custom import Conversation, Message


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
                async def start():
                    return "Hello!"
            """).encode(),
        }
    ],
)
async def test_action_returns_string(user_in_db, add_permission_for_user, chat: Conversation, actions_folder):
    """Test the action decorator without parentheses."""
    add_permission_for_user(user_in_db, "start")

    await chat.send_message("/start")
    response: Message = await chat.get_response()

    assert response.text == "Hello!"


@pytest.mark.asyncio
@pytest.mark.usefixtures("kamihi")
@pytest.mark.parametrize(
    "actions_folder",
    [
        {
            "actions/start/__init__.py": "".encode(),
            "actions/start/start.py": dedent("""\
                from kamihi import bot
                from pathlib import Path
                             
                @bot.action
                async def start() -> Path:
                    return Path("actions/start/file.txt")
            """).encode(),
            "actions/start/file.txt": "This is a file.".encode(),
        }
    ],
)
async def test_action_returns_file(
    user_in_db, add_permission_for_user, chat: Conversation, tg_client: TelegramClient, actions_folder, tmp_path
):
    """Test the action decorator without parentheses."""
    add_permission_for_user(user_in_db, "start")

    await chat.send_message("/start")
    response: Message = await chat.get_response()

    assert response.__getattribute__("file") is not None
    assert response.file.name == "file.txt"

    await tg_client.download_media(response, str(tmp_path))
    dpath = tmp_path / "file.txt"
    assert dpath.exists()
    assert dpath.read_text() == "This is a file."
