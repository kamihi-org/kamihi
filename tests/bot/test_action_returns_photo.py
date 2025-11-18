"""
Test cases for bot actions that return photos.

License:
    MIT

"""

import pytest
from telethon import TelegramClient
from telethon.tl.custom import Conversation, Message

from tests.utils.media import random_image


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
                async def start() -> Path:
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
                async def start() -> bot.Photo:
                    return bot.Photo(Path("actions/start/image.jpg"))
            """,
            "start/image.jpg": random_image(),
        },
    ],
    ids=["implicit", "explicit"],
)
async def test_photo(
    user, add_permission_for_user, chat: Conversation, tg_client: TelegramClient, actions_folder, tmp_path
):
    """Test actions that return a photo."""
    add_permission_for_user(user["telegram_id"], "start")

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
                async def start() -> bot.Photo:
                    return bot.Photo(Path("actions/start/image.jpg"), caption="This is a photo caption.")
            """,
            "start/image.jpg": random_image(),
        },
    ],
)
async def test_photo_captioned(
    user, add_permission_for_user, chat: Conversation, tg_client: TelegramClient, actions_folder, tmp_path
):
    """Test actions that return a photo with a caption."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response: Message = await chat.get_response()

    assert response.text == "This is a photo caption."

    assert response.photo is not None

    path = tmp_path / "image.jpg"
    await tg_client.download_media(response, str(path))
    assert path.exists()
    assert path.stat().st_size > 0
