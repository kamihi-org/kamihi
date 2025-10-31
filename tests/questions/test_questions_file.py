"""
Functional tests for the file type question.

License:
    MIT

"""

import io
import random
import string

import pytest
from telethon.tl.custom import Conversation


@pytest.fixture
def random_text_bytes() -> bytes:
    """Return some small random text bytes for upload."""
    text = "Test file:\n" + "".join(random.choices(string.ascii_letters + string.digits, k=32))
    return text.encode("utf-8")


@pytest.mark.asyncio
@pytest.mark.usefixtures("kamihi")
@pytest.mark.parametrize(
    "actions_folder",
    [
        {
            "start/__init__.py": "",
            "start/start.py": """\
                from typing import Annotated
                from kamihi import bot
                from kamihi.questions import File

                @bot.action
                async def start(f: Annotated[bytes, File(text="Upload a file", return_as="bytes")]):
                    return f"Got {len(f)} bytes."
            """,
        }
    ],
)
async def test_bytes_return(user, add_permission_for_user, chat: Conversation, actions_folder, random_text_bytes):
    """File returned as bytes: action should receive raw bytes and report length."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    prompt = await chat.get_response()
    assert "Upload a file" in prompt.text

    await chat.send_file(io.BytesIO(random_text_bytes), filename="sample.txt")
    final = await chat.get_response()
    assert f"Got {len(random_text_bytes)} bytes." in final.text


@pytest.mark.asyncio
@pytest.mark.usefixtures("kamihi")
@pytest.mark.parametrize(
    "actions_folder",
    [
        {
            "start/__init__.py": "",
            "start/start.py": """\
                from typing import Annotated
                from pathlib import Path
                from kamihi import bot
                from kamihi.questions import File

                @bot.action
                async def start(f: Annotated[Path, File(text="Upload a file", return_as="path")]):
                    return f"Saved with {f.stat().st_size} bytes."
            """,
        }
    ],
)
async def test_path_return(user, add_permission_for_user, chat: Conversation, actions_folder, random_text_bytes):
    """File returned as path: action should receive a Path to saved tempfile and report size."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    prompt = await chat.get_response()
    assert "Upload a file" in prompt.text

    await chat.send_file(io.BytesIO(random_text_bytes), filename="sample.txt")
    final = await chat.get_response()
    # Only assert on file size, not filename
    assert "Saved" in final.text
    assert str(len(random_text_bytes)) in final.text


@pytest.mark.asyncio
@pytest.mark.usefixtures("kamihi")
@pytest.mark.parametrize(
    "actions_folder",
    [
        (
            {
                "start/__init__.py": "",
                "start/start.py": """\
                    from typing import Annotated
                    from kamihi import bot
                    from kamihi.questions import File

                    @bot.action
                    async def start(f: Annotated[bytes, File(
                        text="Upload limited file",
                        max_size=10,
                        error_text="Too large!",
                        return_as="bytes"
                    )]):
                        return f"OK {len(f)}"
                """,
            }
        )
    ],
)
async def test_max_size(user, add_permission_for_user, chat: Conversation, actions_folder):
    """Oversized file yields error_text; then a small file succeeds."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    _ = await chat.get_response()

    # send oversized content
    big = b"X" * 20
    await chat.send_file(io.BytesIO(big), filename="big.txt")
    err = await chat.get_response()
    assert "Too large!" in err.text

    # now send a small valid file
    small = b"ok"
    await chat.send_file(io.BytesIO(small), filename="small.txt")
    final = await chat.get_response()
    assert "OK 2" in final.text


@pytest.mark.asyncio
@pytest.mark.usefixtures("kamihi")
@pytest.mark.parametrize(
    "actions_folder",
    [
        (
            {
                "start/__init__.py": "",
                "start/start.py": """\
                    from typing import Annotated
                    from pathlib import Path
                    from kamihi import bot
                    from kamihi.questions import File

                    @bot.action
                    async def start(f: Annotated[Path, File(
                        text="Upload a text file",
                        allowed_extensions=['txt'],
                        allowed_mime_types=['text/plain']
                    )]):
                        # Return only the file size so tests don't depend on saved filename
                        return f"Accepted {f.stat().st_size}"
                """,
            }
        )
    ],
)
async def test_mime_and_extension_restrictions(
    user, add_permission_for_user, chat: Conversation, actions_folder, random_text_bytes
):
    """
    If a file with a disallowed extension/mime is sent, bot should ignore it (no error) and wait.
    Only after a valid file is sent the action should complete.
    """
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    _ = await chat.get_response()

    # send an invalid extension first (bot should ignore it and not reply with an error)
    await chat.send_file(io.BytesIO(random_text_bytes), filename="bad.jpg")

    # immediately send a valid file; the final response should reference the valid upload size (stable)
    await chat.send_file(io.BytesIO(random_text_bytes), filename="good.txt")
    final = await chat.get_response()
    assert "Accepted" in final.text
    assert str(len(random_text_bytes)) in final.text
