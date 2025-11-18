"""
Test cases for bot actions that return voice notes.

License:
    MIT

"""
import pytest
from telethon import TelegramClient
from telethon.tl.custom import Conversation, Message

from tests.utils.media import random_voice_note_path


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
                    return Path("actions/start/voice.mp3")
            """,
            "start/voice.mp3": random_voice_note_path().read_bytes(),
        },
        {
            "start/__init__.py": "",
            "start/start.py": """\
                from kamihi import bot
                from pathlib import Path
                             
                @bot.action
                async def start() -> bot.Voice:
                    return bot.Voice(Path("actions/start/voice.mp3"))
            """,
            "start/voice.mp3": random_voice_note_path().read_bytes(),
        },
    ],
    ids=["implicit", "explicit"],
)
async def test_voice(
    user, add_permission_for_user, chat: Conversation, tg_client: TelegramClient, actions_folder, tmp_path
):
    """Test actions that returns a voice note."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response: Message = await chat.get_response()

    assert response.voice is not None

    path = tmp_path / "voice.mp3"
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
                
                @bot.action
                async def start() -> bot.Voice:
                    return bot.Voice(Path("actions/start/voice.mp3"), caption="This is a voice note caption.")
            """,
            "start/voice.mp3": random_voice_note_path().read_bytes(),
        },
    ],
)
async def test_voice_captioned(
    user, add_permission_for_user, chat: Conversation, tg_client: TelegramClient, actions_folder, tmp_path
):
    """Test actions that return a voice note with a caption."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response: Message = await chat.get_response()

    assert response.text == "This is a voice note caption."

    assert response.voice is not None

    path = tmp_path / "voice.mp3"
    await tg_client.download_media(response, str(path))
    assert path.exists()
    assert path.stat().st_size > 0
