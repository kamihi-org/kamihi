"""
Test cases for bot actions that return audios.

License:
    MIT

"""
import pytest
from telethon import TelegramClient
from telethon.tl.custom import Conversation, Message

from tests.utils.media import random_audio_path


@pytest.mark.asyncio
@pytest.mark.timeout(120)
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
                    return Path("actions/start/audio.mp3")
            """,
            "start/audio.mp3": random_audio_path().read_bytes(),
        },
        {
            "start/__init__.py": "",
            "start/start.py": """\
                from kamihi import bot
                from pathlib import Path
                             
                @bot.action
                async def start() -> bot.Audio:
                    return bot.Audio(Path("actions/start/audio.mp3"))
            """,
            "start/audio.mp3": random_audio_path().read_bytes(),
        },
    ],
    ids=["implicit", "explicit"],
)
async def test_audio(
    user, add_permission_for_user, chat: Conversation, tg_client: TelegramClient, actions_folder, tmp_path
):
    """Test actions that return an audio."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response: Message = await chat.get_response()

    assert response.audio is not None

    path = tmp_path / "audio.mp3"
    await tg_client.download_media(response, str(path))
    assert path.exists()
    assert path.stat().st_size > 0


@pytest.mark.asyncio
@pytest.mark.timeout(120)
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
                async def start() -> bot.Audio:
                    return bot.Audio(Path("actions/start/audio.mp3"), caption="This is an audio caption.")
            """,
            "start/audio.mp3": random_audio_path().read_bytes(),
        },
    ],
)
async def test_captioned(
    user, add_permission_for_user, chat: Conversation, tg_client: TelegramClient, actions_folder, tmp_path
):
    """Test actions that return an audio with a caption."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response: Message = await chat.get_response()

    assert response.text == "This is an audio caption."

    assert response.audio is not None

    path = tmp_path / "audio.mp3"
    await tg_client.download_media(response, str(path))
    assert path.exists()
    assert path.stat().st_size > 0
