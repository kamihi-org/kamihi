"""
Functional tests for action returns.

License:
    MIT
"""

import pytest
from telethon import TelegramClient
from telethon.tl.custom import Conversation, Message

from tests.conftest import random_image


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
async def test_action_returns_string(user_in_db, add_permission_for_user, chat: Conversation, actions_folder):
    """Test actions that return a string."""
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
                from typing import Annotated
                             
                @bot.action
                async def start() -> Annotated[Path, bot.Document()]:
                    return Path("actions/start/file.txt")
            """,
            "start/file.txt": "This is a file.",
        },
        {
            "start/__init__.py": "",
            "start/start.py": """\
                from kamihi import bot
                from pathlib import Path
                from typing import Annotated
                             
                @bot.action
                async def start():
                    return bot.Document(Path("actions/start/file.txt"))
            """,
            "start/file.txt": "This is a file.",
        },
        {
            "start/__init__.py": "",
            "start/start.py": """\
                from kamihi import bot
                from pathlib import Path
                from typing import Annotated
                             
                @bot.action
                async def start() -> bot.Document:
                    return bot.Document(Path("actions/start/file.txt"))
            """,
            "start/file.txt": "This is a file.",
        },
    ],
    ids=["only_path", "annotated", "class", "class_ra"],
)
async def test_action_returns_file(
    user_in_db, add_permission_for_user, chat: Conversation, tg_client: TelegramClient, actions_folder, tmp_path
):
    """Test actions that return a file."""
    add_permission_for_user(user_in_db, "start")

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
                from typing import Annotated
                             
                @bot.action
                async def start() -> Annotated[Path, bot.Document(caption="This is a file caption.")]:
                    return Path("actions/start/file.txt")
            """,
            "start/file.txt": "This is a file.",
        },
        {
            "start/__init__.py": "",
            "start/start.py": """\
                from kamihi import bot
                from pathlib import Path
                from typing import Annotated
                             
                @bot.action
                async def start():
                    return bot.Document(Path("actions/start/file.txt"), caption="This is a file caption.")
            """,
            "start/file.txt": "This is a file.",
        },
        {
            "start/__init__.py": "",
            "start/start.py": """\
                from kamihi import bot
                from pathlib import Path
                from typing import Annotated
                             
                @bot.action
                async def start() -> bot.Document:
                    return bot.Document(Path("actions/start/file.txt"), caption="This is a file caption.")
            """,
            "start/file.txt": "This is a file.",
        },
    ],
    ids=["annotated", "class", "class_ra"],
)
async def test_action_returns_file_captioned(
    user_in_db, add_permission_for_user, chat: Conversation, tg_client: TelegramClient, actions_folder, tmp_path
):
    """Test actions that return a file with a caption."""
    add_permission_for_user(user_in_db, "start")

    await chat.send_message("/start")
    response: Message = await chat.get_response()

    assert response.text == "This is a file caption."

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
                from typing import Annotated
                             
                @bot.action
                async def start() -> Annotated[Path, bot.Photo()]:
                    return Path("actions/start/image.jpg")
            """,
            "start/image.jpg": random_image(),
        },
        {
            "start/__init__.py": "",
            "start/start.py": """\
                from kamihi import bot
                from pathlib import Path
                from typing import Annotated
                             
                @bot.action
                async def start():
                    return bot.Photo(Path("actions/start/image.jpg"))
            """,
            "start/image.jpg": random_image(),
        },
        {
            "start/__init__.py": "",
            "start/start.py": """\
                from kamihi import bot
                from pathlib import Path
                from typing import Annotated
                             
                @bot.action
                async def start() -> bot.Photo:
                    return bot.Photo(Path("actions/start/image.jpg"))
            """,
            "start/image.jpg": random_image(),
        },
    ],
    ids=["annotated", "class", "class_ra"],
)
async def test_action_returns_photo(
    user_in_db, add_permission_for_user, chat: Conversation, tg_client: TelegramClient, actions_folder, tmp_path
):
    """Test that the action sends a photo to Telegram when a Path is returned and the bot.Photo annotation is used."""
    add_permission_for_user(user_in_db, "start")

    await chat.send_message("/start")
    response: Message = await chat.get_response()

    assert response.photo is not None

    path = tmp_path / "image.jpg"
    await tg_client.download_media(response, str(path))
    assert path.exists()
    assert path.stat().st_size > 0


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
                from typing import Annotated
                             
                @bot.action
                async def start() -> Annotated[Path, bot.Photo(caption="This is a photo caption.")]:
                    return Path("actions/start/image.jpg")
            """,
            "start/image.jpg": random_image(),
        },
        {
            "start/__init__.py": "",
            "start/start.py": """\
                from kamihi import bot
                from pathlib import Path
                from typing import Annotated
                             
                @bot.action
                async def start():
                    return bot.Photo(Path("actions/start/image.jpg"), caption="This is a photo caption.")
            """,
            "start/image.jpg": random_image(),
        },
        {
            "start/__init__.py": "",
            "start/start.py": """\
                from kamihi import bot
                from pathlib import Path
                from typing import Annotated
                             
                @bot.action
                async def start() -> bot.Photo:
                    return bot.Photo(Path("actions/start/image.jpg"), caption="This is a photo caption.")
            """,
            "start/image.jpg": random_image(),
        },
    ],
    ids=["annotated", "class", "class_ra"],
)
async def test_action_returns_photo_captioned(
    user_in_db, add_permission_for_user, chat: Conversation, tg_client: TelegramClient, actions_folder, tmp_path
):
    """Test that the action sends a photo with a caption to Telegram when a Path is returned and the bot.Photo annotation is used."""
    add_permission_for_user(user_in_db, "start")

    await chat.send_message("/start")
    response: Message = await chat.get_response()

    assert response.text == "This is a photo caption."

    assert response.photo is not None

    path = tmp_path / "image.jpg"
    await tg_client.download_media(response, str(path))
    assert path.exists()
    assert path.stat().st_size > 0
