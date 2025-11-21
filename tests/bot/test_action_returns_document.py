"""
Test cases for bot actions that return documents.

License:
    MIT

"""

import pytest
from telethon import TelegramClient
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
                from pathlib import Path
                             
                @bot.action
                async def start() -> Path:
                    return Path("actions/start/file.txt")
            """,
            "start/file.txt": "This is a file.",
        },
        {
            "start/__init__.py": "",
            "start/start.py": """\
                from kamihi import bot
                from pathlib import Path
                             
                @bot.action
                async def start() -> bot.Document:
                    return bot.Document(Path("actions/start/file.txt"))
            """,
            "start/file.txt": "This is a file.",
        },
    ],
    ids=["implicit", "explicit"],
)
async def test_document(
    user, add_permission_for_user, chat: Conversation, tg_client: TelegramClient, actions_folder, tmp_path
):
    """Test actions that returns documents."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response: Message = await chat.get_response()

    assert response.document is not None
    assert response.document.mime_type == "text/plain"

    await tg_client.download_media(response, str(tmp_path))
    dpath = tmp_path / "file.txt"
    assert dpath.exists()
    assert dpath.read_text() == "This is a file."


@pytest.mark.asyncio
@pytest.mark.usefixtures("kamihi")
@pytest.mark.parametrize(
    "actions_folder",
    [
        {
            "start/__init__.py": "",
            "start/start.py": """\
                from kamihi import bot
                from pathlib import Path
                             
                @bot.action
                async def start() -> bot.Document:
                    return bot.Document(Path("actions/start/file.txt"), caption="This is a file caption.")
            """,
            "start/file.txt": "This is a file.",
        },
    ],
)
async def test_document_captioned(
    user, add_permission_for_user, chat: Conversation, tg_client: TelegramClient, actions_folder, tmp_path
):
    """Test actions that return a file with a caption."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response: Message = await chat.get_response()

    assert response.text == "This is a file caption."

    assert response.document is not None
    assert response.document.mime_type == "text/plain"

    await tg_client.download_media(response, str(tmp_path))
    dpath = tmp_path / "file.txt"
    assert dpath.exists()
    assert dpath.read_text() == "This is a file."
