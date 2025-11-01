"""
Functional tests for the image type question.

License:
    MIT

"""
import io
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest
from PIL import Image as PILImage
from telethon.tl.custom import Conversation
from tests.utils.media import random_image


def reencode_jpeg(img_b: bytes, size: tuple[int, int], quality: int = 85) -> bytes:
    """Re-encode provided image bytes to specific size/quality (deterministic dimensions)."""
    img = PILImage.open(io.BytesIO(img_b)).convert("RGB").resize(size)
    out = io.BytesIO()
    img.save(out, format="JPEG", quality=quality, optimize=True)
    return out.getvalue()


def reencode_png(img_b: bytes, size: tuple[int, int]) -> bytes:
    """Re-encode provided image bytes to PNG at a specific size."""
    img = PILImage.open(io.BytesIO(img_b)).convert("RGB").resize(size)
    out = io.BytesIO()
    img.save(out, format="PNG", optimize=True)
    return out.getvalue()


@pytest.fixture
def small_image_bytes() -> bytes:
    """Deterministic small photo that Telegram won't resize (64x64)."""
    return reencode_jpeg(random_image(), (64, 64), quality=85)


@pytest.fixture
def tiny_image_bytes() -> bytes:
    """Very tiny image for max size success path."""
    return reencode_jpeg(random_image(), (16, 16), quality=40)


@pytest.fixture
def large_image_bytes() -> bytes:
    """Very large image for max size failure path."""
    return reencode_jpeg(random_image(), (1920, 1080), quality=95)


@pytest.fixture
def small_image_path_jpeg(small_image_bytes) -> Path:
    with NamedTemporaryFile(suffix=".jpeg", delete=False) as tmp:
        tmp.write(small_image_bytes)
        p = Path(tmp.name)
    try:
        yield p
    finally:
        p.unlink(missing_ok=True)


@pytest.fixture
def tiny_image_path_jpeg(tiny_image_bytes) -> Path:
    with NamedTemporaryFile(suffix=".jpeg", delete=False) as tmp:
        tmp.write(tiny_image_bytes)
        p = Path(tmp.name)
    try:
        yield p
    finally:
        p.unlink(missing_ok=True)


@pytest.fixture
def large_image_path_jpeg(large_image_bytes) -> Path:
    with NamedTemporaryFile(suffix=".jpeg", delete=False) as tmp:
        tmp.write(large_image_bytes)
        p = Path(tmp.name)
    try:
        yield p
    finally:
        p.unlink(missing_ok=True)


@pytest.fixture
def small_image_path_png(small_image_bytes) -> Path:
    """PNG path for invalid-extension test."""
    png_bytes = reencode_png(small_image_bytes, (64, 64))
    with NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp.write(png_bytes)
        p = Path(tmp.name)
    try:
        yield p
    finally:
        p.unlink(missing_ok=True)


@pytest.mark.asyncio
@pytest.mark.usefixtures("kamihi")
@pytest.mark.parametrize(
    "actions_folder",
    [
        {
            "start/__init__.py": "",
            "start/start.py": """\
                from typing import Annotated
                from io import BytesIO
                from PIL import Image as PILImage
                from kamihi import bot
                from kamihi.questions import Image

                @bot.action
                async def start(img: Annotated[bytes, Image(text="Send an image", return_as="bytes")]):
                    w, h = PILImage.open(BytesIO(img)).size
                    return f"Image size: {w}x{h}"
            """,
        }
    ],
)
async def test_bytes_return(
    user, add_permission_for_user, chat: Conversation, actions_folder, small_image_path_jpeg
):
    """Image returned as bytes: action should report dimensions."""
    add_permission_for_user(user["telegram_id"], "start")
    w, h = PILImage.open(small_image_path_jpeg).size

    await chat.send_message("/start")
    prompt = await chat.get_response()
    assert "Send an image" in prompt.text

    await chat.send_file(small_image_path_jpeg)
    final = await chat.get_response()
    assert f"Image size: {w}x{h}" in final.text


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
                from PIL import Image as PILImage
                from kamihi import bot
                from kamihi.questions import Image

                @bot.action
                async def start(img: Annotated[Path, Image(text="Send an image", return_as="path")]):
                    w, h = PILImage.open(img).size
                    return f"Saved image size: {w}x{h}"
            """,
        }
    ],
)
async def test_path_return(
    user, add_permission_for_user, chat: Conversation, actions_folder, small_image_path_jpeg
):
    """Image returned as path: action should report dimensions."""
    add_permission_for_user(user["telegram_id"], "start")
    w, h = PILImage.open(small_image_path_jpeg).size

    await chat.send_message("/start")
    prompt = await chat.get_response()
    assert "Send an image" in prompt.text

    await chat.send_file(small_image_path_jpeg)
    final = await chat.get_response()
    assert f"Saved image size: {w}x{h}" in final.text


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
                from kamihi.questions import Image

                @bot.action
                async def start(img: Annotated["PIL.Image.Image", Image(text="Send an image", return_as="pil")]):
                    return f"Image size: {img.size[0]}x{img.size[1]}"
            """,
        }
    ],
)
async def test_pil_return(
    user, add_permission_for_user, chat: Conversation, actions_folder, small_image_path_jpeg
):
    """Image returned as PIL: action should report dimensions."""
    add_permission_for_user(user["telegram_id"], "start")
    w, h = PILImage.open(small_image_path_jpeg).size

    await chat.send_message("/start")
    prompt = await chat.get_response()
    assert "Send an image" in prompt.text

    await chat.send_file(small_image_path_jpeg)
    final = await chat.get_response()
    assert f"Image size: {w}x{h}" in final.text


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
                    from io import BytesIO
                    from PIL import Image as PILImage
                    from kamihi import bot
                    from kamihi.questions import Image

                    @bot.action
                    async def start(img: Annotated[bytes, Image(
                        text="Send small image",
                        max_size=2000,
                        error_text="Too large!",
                        return_as="bytes"
                    )]):
                        w, h = PILImage.open(BytesIO(img)).size
                        return f"OK {w}x{h}"
                """,
            }
        )
    ],
)
async def test_max_size(
    user, add_permission_for_user, chat: Conversation, actions_folder, large_image_path_jpeg, tiny_image_path_jpeg
):
    """Oversized image yields error_text; then a tiny image succeeds. Validate by dimensions."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    _ = await chat.get_response()

    await chat.send_file(large_image_path_jpeg)
    err = await chat.get_response()
    assert "Too large!" in err.text

    await chat.send_file(tiny_image_path_jpeg)
    final = await chat.get_response()
    assert "OK 16x16" in final.text


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
                    from PIL import Image as PILImage
                    from kamihi import bot
                    from kamihi.questions import Image

                    @bot.action
                    async def start(img: Annotated[Path, Image(
                        text="Send a JPEG image",
                        allowed_extensions=['jpg', 'jpeg'],
                        allowed_mime_types=['image/jpeg']
                    )]):
                        w, h = PILImage.open(img).size
                        return f"Accepted {w}x{h}"
                """,
            }
        )
    ],
)
async def test_mime_and_extension_restrictions(
    user, add_permission_for_user, chat: Conversation, actions_folder, small_image_path_png, small_image_path_jpeg
):
    """
    If an image with a disallowed extension/mime is sent, bot should ignore it (no error) and wait.
    Only after a valid image is sent the action should complete. Validate by dimensions.
    """
    add_permission_for_user(user["telegram_id"], "start")
    w, h = PILImage.open(small_image_path_jpeg).size

    await chat.send_message("/start")
    _ = await chat.get_response()

    # send an invalid extension first (bot should ignore it and not reply with an error)
    await chat.send_file(small_image_path_png)

    # immediately send a valid image; the final response should reflect the valid upload
    await chat.send_file(small_image_path_jpeg)
    final = await chat.get_response()
    assert f"Accepted {w}x{h}" in final.text
