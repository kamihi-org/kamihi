"""
Common fixtures and utilities for testing.

License:
    MIT

"""

import io
import random
from pathlib import Path

import numpy as np
import pytest
from PIL import Image
from telegram.constants import FileSizeLimit


def random_image() -> bytes:
    """Fixture to provide a random JPEG image as bytes."""
    while True:
        width = np.random.randint(1, 10000)
        height = np.random.randint(1, 10000)

        if any(
            [
                width + height < 10000,
                width + height > 10000,
                max(width, height) / min(width, height) > 20,
            ]
        ):
            continue

        pixel_data = np.random.randint(0, 256, size=(height, width, 3), dtype=np.uint8)
        img = Image.fromarray(pixel_data, "RGB")
        img_bytes_io = io.BytesIO()
        img.save(img_bytes_io, format="JPEG", quality=85, optimize=True)

        file_size_bytes = img_bytes_io.tell()
        if not file_size_bytes <= FileSizeLimit.PHOTOSIZE_UPLOAD:
            continue

        return img_bytes_io.getvalue()


@pytest.fixture
def random_video_path() -> Path:
    """Fixture to provide a random video as bytes."""
    return random.choice(list(Path("tests/static/videos").glob("*.mp4")))
