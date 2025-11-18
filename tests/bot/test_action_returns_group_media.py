"""
Test cases for bot actions that return a list of media that can be grouped.

License:
    MIT

"""

import pytest
from telethon.tl.custom import Conversation, Message

from tests.utils.media import random_image, random_video_path, random_audio_path


@pytest.mark.asyncio
@pytest.mark.usefixtures("kamihi")
@pytest.mark.parametrize(
    "actions_folder,number_of_messages",
    [
        (
            {
                "start/__init__.py": "",
                "start/start.py": """\
                    from pathlib import Path
                    from kamihi import bot
                
                    @bot.action
                    async def start() -> list[bot.Photo]:
                        return [
                            bot.Photo(Path("actions/start/image.jpg")),
                            bot.Photo(Path("actions/start/image.jpg")),
                            bot.Photo(Path("actions/start/image.jpg")),
                        ]
                """,
                "start/image.jpg": random_image(),
            },
            3,
        ),
        (
            {
                "start/__init__.py": "",
                "start/start.py": """\
                    from pathlib import Path
                    from kamihi import bot
                
                    @bot.action
                    async def start() -> list[bot.Photo | bot.Video]:
                        return [
                            bot.Photo(Path("actions/start/image.jpg")),
                            bot.Video(Path("actions/start/video.mp4")),
                            bot.Photo(Path("actions/start/image.jpg")),
                            bot.Video(Path("actions/start/video.mp4")),
                        ]
                """,
                "start/image.jpg": random_image(),
                "start/video.mp4": random_video_path().read_bytes(),
            },
            4,
        ),
        (
            {
                "start/__init__.py": "",
                "start/start.py": """\
                    from pathlib import Path
                    from kamihi import bot
                
                    @bot.action
                    async def start() -> list[bot.Audio]:
                        return [
                            bot.Audio(Path("actions/start/audio.mp3")),
                            bot.Audio(Path("actions/start/audio.mp3")),
                            bot.Audio(Path("actions/start/audio.mp3")),
                        ]
                """,
                "start/audio.mp3": random_audio_path().read_bytes(),
            },
            3,
        ),
        (
            {
                "start/__init__.py": "",
                "start/start.py": """\
                    from pathlib import Path
                    from kamihi import bot
                
                    @bot.action
                    async def start() -> list[bot.Document]:
                        return [
                            bot.Document(Path("actions/start/file.txt")),
                            bot.Document(Path("actions/start/file.txt")),
                            bot.Document(Path("actions/start/file.txt")),
                        ]
                """,
                "start/file.txt": "This is a file.",
            },
            3,
        ),
    ],
)
async def test_group_media(user, add_permission_for_user, chat: Conversation, actions_folder, number_of_messages):
    """Test actions that return multiple messages."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")

    ids = []
    for _ in range(number_of_messages):
        response: Message = await chat.get_response()
        assert response.media is not None
        ids.append(response.grouped_id)

    assert all(i == ids[0] for i in ids)
