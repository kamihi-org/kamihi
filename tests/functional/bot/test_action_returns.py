"""
Functional tests for action returns.

License:
    MIT
"""

import random

import pytest
from telethon import TelegramClient
from telethon.tl.custom import Conversation, Message

from kamihi.bot.media import Location
from tests.conftest import random_image, random_video_path, random_audio


def random_location() -> Location:
    """
    Generates a random location with latitude and longitude.

    Returns:
        tuple[float, float]: A tuple containing latitude and longitude.

    """
    latitude = random.uniform(-90.0, 90.0)
    longitude = random.uniform(-180.0, 180.0)
    return Location(latitude=latitude, longitude=longitude)


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
                    async def start():
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
                    async def start():
                        return ["This is a message", bot.Photo(Path("actions/start/image.jpg"), caption="and this is a photo!")]
                """,
                "start/image.jpg": random_image(),
            },
            ["This is a message", "and this is a photo!"],
        ),
    ],
)
async def test_action_returns_list(user_in_db, add_permission_for_user, chat: Conversation, actions_folder, messages):
    """Test actions that return multiple messages."""
    add_permission_for_user(user_in_db, "start")

    await chat.send_message("/start")

    for message in messages:
        response: Message = await chat.get_response()
        assert response.text == message


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
                async def start() -> Annotated[Path, bot.Video()]:
                    return Path("actions/start/video.mp4")
            """,
            "start/video.mp4": random_video_path().read_bytes(),
        },
        {
            "start/__init__.py": "",
            "start/start.py": """\
                from kamihi import bot
                from pathlib import Path
                from typing import Annotated
                             
                @bot.action
                async def start():
                    return bot.Video(Path("actions/start/video.mp4"))
            """,
            "start/video.mp4": random_video_path().read_bytes(),
        },
        {
            "start/__init__.py": "",
            "start/start.py": """\
                from kamihi import bot
                from pathlib import Path
                from typing import Annotated
                             
                @bot.action
                async def start() -> bot.Video:
                    return bot.Video(Path("actions/start/video.mp4"))
            """,
            "start/video.mp4": random_video_path().read_bytes(),
        },
    ],
    ids=["annotated", "class", "class_ra"],
)
async def test_action_returns_video(
    user_in_db, add_permission_for_user, chat: Conversation, tg_client: TelegramClient, actions_folder, tmp_path
):
    """Test that the action sends a video to Telegram when a Path is returned and the bot.Video annotation is used."""
    add_permission_for_user(user_in_db, "start")

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
                from typing import Annotated
                             
                @bot.action
                async def start() -> Annotated[Path, bot.Video(caption="This is a video caption.")]:
                    return Path("actions/start/video.mp4")
            """,
            "start/video.mp4": random_video_path().read_bytes(),
        },
        {
            "start/__init__.py": "",
            "start/start.py": """\
                from kamihi import bot
                from pathlib import Path
                from typing import Annotated
                             
                @bot.action
                async def start():
                    return bot.Video(Path("actions/start/video.mp4"), caption="This is a video caption.")
            """,
            "start/video.mp4": random_video_path().read_bytes(),
        },
        {
            "start/__init__.py": "",
            "start/start.py": """\
                from kamihi import bot
                from pathlib import Path
                from typing import Annotated
                             
                @bot.action
                async def start() -> bot.Video:
                    return bot.Video(Path("actions/start/video.mp4"), caption="This is a video caption.")
            """,
            "start/video.mp4": random_video_path().read_bytes(),
        },
    ],
    ids=["annotated", "class", "class_ra"],
)
async def test_action_returns_video_captioned(
    user_in_db, add_permission_for_user, chat: Conversation, tg_client: TelegramClient, actions_folder, tmp_path
):
    """Test that the action sends a video with a caption to Telegram when a Path is returned and the bot.Video annotation is used."""
    add_permission_for_user(user_in_db, "start")

    await chat.send_message("/start")
    response: Message = await chat.get_response()

    assert response.text == "This is a video caption."

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
                from typing import Annotated
                             
                @bot.action
                async def start() -> Annotated[Path, bot.Audio()]:
                    return Path("actions/start/audio.mp3")
            """,
            "start/audio.mp3": random_audio(),
        },
        {
            "start/__init__.py": "",
            "start/start.py": """\
                from kamihi import bot
                from pathlib import Path
                from typing import Annotated
                             
                @bot.action
                async def start():
                    return bot.Audio(Path("actions/start/audio.mp3"))
            """,
            "start/audio.mp3": random_audio(),
        },
        {
            "start/__init__.py": "",
            "start/start.py": """\
                from kamihi import bot
                from pathlib import Path
                from typing import Annotated
                             
                @bot.action
                async def start() -> bot.Audio:
                    return bot.Audio(Path("actions/start/audio.mp3"))
            """,
            "start/audio.mp3": random_audio(),
        },
    ],
    ids=["annotated", "class", "class_ra"],
)
async def test_action_returns_audio(
    user_in_db, add_permission_for_user, chat: Conversation, tg_client: TelegramClient, actions_folder, tmp_path
):
    """Test that the action sends an audio to Telegram when a Path is returned and the bot.Audio annotation is used."""
    add_permission_for_user(user_in_db, "start")

    await chat.send_message("/start")
    response: Message = await chat.get_response()

    assert response.audio is not None

    path = tmp_path / "audio.mp3"
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
                async def start() -> Annotated[Path, bot.Audio(caption="This is an audio caption.")]:
                    return Path("actions/start/audio.mp3")
            """,
            "start/audio.mp3": random_audio(),
        },
        {
            "start/__init__.py": "",
            "start/start.py": """\
                from kamihi import bot
                from pathlib import Path
                from typing import Annotated
                             
                @bot.action
                async def start():
                    return bot.Audio(Path("actions/start/audio.mp3"), caption="This is an audio caption.")
            """,
            "start/audio.mp3": random_audio(),
        },
        {
            "start/__init__.py": "",
            "start/start.py": """\
                from kamihi import bot
                from pathlib import Path
                from typing import Annotated
                             
                @bot.action
                async def start() -> bot.Audio:
                    return bot.Audio(Path("actions/start/audio.mp3"), caption="This is an audio caption.")
            """,
            "start/audio.mp3": random_audio(),
        },
    ],
    ids=["annotated", "class", "class_ra"],
)
async def test_action_returns_audio_captioned(
    user_in_db, add_permission_for_user, chat: Conversation, tg_client: TelegramClient, actions_folder, tmp_path
):
    """Test that the action sends an audio with a caption to Telegram when a Path is returned and the bot.Audio annotation is used."""
    add_permission_for_user(user_in_db, "start")

    await chat.send_message("/start")
    response: Message = await chat.get_response()

    assert response.text == "This is an audio caption."

    assert response.audio is not None

    path = tmp_path / "audio.mp3"
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
            "start/start.py": f"""\
                from kamihi import bot
                             
                @bot.action
                async def start():
                    return bot.Location(latitude={random_location().latitude}, longitude={random_location().latitude})
            """,
        },
        {
            "start/__init__.py": "",
            "start/start.py": f"""\
                from kamihi import bot
                from typing import Annotated
                             
                @bot.action
                async def start() -> Annotated[str, bot.Location]:
                    return "{random_location().latitude}, {random_location().latitude}"
            """,
        },
        {
            "start/__init__.py": "",
            "start/start.py": f"""\
                from kamihi import bot
                from typing import Annotated
                             
                @bot.action
                async def start() -> Annotated[tuple, bot.Location]:
                    return {random_location().latitude}, {random_location().latitude}
            """,
        },
        {
            "start/__init__.py": "",
            "start/start.py": f"""\
                from kamihi import bot
                from typing import Annotated
                             
                @bot.action
                async def start() -> Annotated[list, bot.Location]:
                    return [{random_location().latitude}, {random_location().latitude}]
            """,
        },
        {
            "start/__init__.py": "",
            "start/start.py": f"""\
                from kamihi import bot
                from typing import Annotated
                             
                @bot.action
                async def start() -> Annotated[dict, bot.Location]:
                    return {{"latitude": {random_location().latitude}, "longitude": {random_location().latitude}}}
            """,
        },
    ],
    ids=["class", "annotated_string", "annotated_tuple", "annotated_list", "annotated_dict"],
)
async def test_action_returns_location(user_in_db, add_permission_for_user, chat: Conversation, actions_folder):
    """Test that the action sends a location to Telegram when a Location is returned."""
    add_permission_for_user(user_in_db, "start")

    await chat.send_message("/start")
    response: Message = await chat.get_response()

    assert response.geo is not None
