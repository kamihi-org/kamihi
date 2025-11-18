import pytest
from telethon import TelegramClient
from telethon.tl.custom import Conversation, Message

from tests.utils.media import random_video_path


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
                    return Path("actions/start/video.mp4")
            """,
            "start/video.mp4": random_video_path().read_bytes(),
        },
        {
            "start/__init__.py": "",
            "start/start.py": """\
                from kamihi import bot
                from pathlib import Path
                
                @bot.action
                async def start() -> bot.Video:
                    return bot.Video(Path("actions/start/video.mp4"))
            """,
            "start/video.mp4": random_video_path().read_bytes(),
        },
    ],
    ids=["implicit", "explicit"],
)
async def test_video(
    user, add_permission_for_user, chat: Conversation, tg_client: TelegramClient, actions_folder, tmp_path
):
    """Test actions that return a video."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response: Message = await chat.get_response()

    assert response.video is not None

    path = tmp_path / "video.mp4"
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
                async def start() -> bot.Video:
                    return bot.Video(Path("actions/start/video.mp4"), caption="This is a video caption.")
            """,
            "start/video.mp4": random_video_path().read_bytes(),
        },
    ],
)
async def test_video_captioned(
    user, add_permission_for_user, chat: Conversation, tg_client: TelegramClient, actions_folder, tmp_path
):
    """Test actions that return a video with a caption."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response: Message = await chat.get_response()

    assert response.text == "This is a video caption."

    assert response.video is not None

    path = tmp_path / "video.mp4"
    await tg_client.download_media(response, str(path))
    assert path.exists()
    assert path.stat().st_size > 0
