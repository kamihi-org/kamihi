"""
Common fixtures and utilities for testing.

License:
    MIT

"""

import io
import random
from pathlib import Path

import numpy as np
from PIL import Image


def random_image() -> bytes:
    """Fixture to provide a random JPEG image as bytes."""
    # Pre-computed valid (width, height) pairs for sum=10000 and aspect ratio <=20
    # This eliminates computation overhead and ensures fast, reliable generation
    valid_pairs = [
        (476, 9524),
        (500, 9500),
        (600, 9400),
        (700, 9300),
        (800, 9200),
        (900, 9100),
        (1000, 9000),
        (1200, 8800),
        (1500, 8500),
        (2000, 8000),
        (2500, 7500),
        (3000, 7000),
        (3500, 6500),
        (4000, 6000),
        (4500, 5500),
        (5000, 5000),
        (5500, 4500),
        (6000, 4000),
        (6500, 3500),
        (7000, 3000),
        (7500, 2500),
        (8000, 2000),
        (8500, 1500),
        (8800, 1200),
        (9000, 1000),
        (9100, 900),
        (9200, 800),
        (9300, 700),
        (9400, 600),
        (9500, 500),
        (9524, 476),
    ]

    # Randomly select a pair
    width, height = random.choice(valid_pairs)

    # Conservative scaling to ensure file size compliance
    max_pixels = 1_500_000
    if width * height > max_pixels:
        scale = (max_pixels / (width * height)) ** 0.5
        width = int(width * scale)
        height = int(height * scale)

    # Generate pixel data efficiently
    pixel_data = np.random.randint(0, 256, size=(height, width, 3), dtype=np.uint8)
    img = Image.fromarray(pixel_data, "RGB")
    img_bytes_io = io.BytesIO()
    img.save(img_bytes_io, format="JPEG", quality=85, optimize=True)

    return img_bytes_io.getvalue()


def random_video_path() -> Path:
    """Fixture to provide a random video as bytes."""
    return random.choice(list(Path("tests/static/videos").glob("*.mp4")))


def random_audio_path() -> Path:
    """
    Fixture to provide random audio data.

    It provides what Telegram considers an audio file, as opposed to a voice note, to ensure
    that the file is not considered a voice note by Telegram.
    """
    return random.choice(list(Path("tests/static/audios").glob("audio_*")))


def random_voice_note_path() -> Path:
    """
    Fixture to provide random voice note data.

    It provides what Telegram considers a voice note, ensuring that the file is small enough
    to be considered a voice note instead of a regular audio file.
    """
    return random.choice(list(Path("tests/static/audios").glob("voice_*")))
