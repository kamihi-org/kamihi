"""
Common fixtures and utilities for testing.

License:
    MIT

"""

import io
import random
from pathlib import Path
from typing import Literal

import numpy as np
import pytest
from PIL import Image
from pydub import AudioSegment
from telegram.constants import FileSizeLimit


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


def random_audio_generator(
    output_format: Literal["mp3", "m4a"] = "mp3",
    min_size_bytes: int | None = None,
    max_size_bytes: int | None = None,
    max_attempts: int = 8,
) -> bytes:
    """
    Generates random audio data as bytes in MP3 or M4A format.

    Optimized for speed using pure white noise generation - the fastest approach
    when size constraints are involved, while still being very fast without constraints.

    Args:
        output_format (Literal["mp3", "m4a"]): The format of the output audio file.
        min_size_bytes (int | None): Minimum file size in bytes. If None, no minimum.
        max_size_bytes (int | None): Maximum file size in bytes. If None, no maximum.
        max_attempts (int): Maximum attempts to generate audio within size constraints.

    Returns:
        bytes: The generated audio data in the specified format.
    """
    sample_rate = 22050

    if output_format == "mp3":
        bytes_per_second = 4000
    else:
        bytes_per_second = 5000

    for attempt in range(max_attempts):
        if min_size_bytes or max_size_bytes:
            if min_size_bytes:
                min_duration = max(0.5, (min_size_bytes * 1.1) / bytes_per_second)
            else:
                min_duration = 0.5

            if max_size_bytes:
                max_duration = min(20.0, (max_size_bytes * 0.9) / bytes_per_second)
            else:
                max_duration = 5.0

            duration = random.uniform(min_duration, min(max_duration, min_duration * 1.1))
        else:
            duration = random.uniform(1.0, 2.0)

        num_samples = int(sample_rate * duration)

        # Fastest possible: just random noise
        audio_data = np.random.randint(-8192, 8191, num_samples, dtype=np.int16)

        audio_segment = AudioSegment(
            audio_data.tobytes(),
            frame_rate=sample_rate,
            sample_width=2,
            channels=1,
        )

        audio_bytes_io = io.BytesIO()
        export_format = "ipod" if output_format == "m4a" else output_format
        audio_segment.export(audio_bytes_io, format=export_format, parameters=["-q:a", "9", "-ac", "1"])

        result = audio_bytes_io.getvalue()
        result_size = len(result)

        if min_size_bytes and result_size < min_size_bytes:
            bytes_per_second = max(bytes_per_second * 0.8, result_size / duration)
            continue
        if max_size_bytes and result_size > max_size_bytes:
            bytes_per_second = min(bytes_per_second * 1.2, result_size / duration)
            continue

        return result

    return result


def random_audio():
    """
    Fixture to provide random audio data.

    It provides what Telegram considers an audio file, as opposed to a voice note, to ensure
    that the file is not considered a voice note by Telegram.
    """
    return random_audio_generator(
        output_format=random.choice(["mp3", "m4a"]),
        min_size_bytes=FileSizeLimit.VOICE_NOTE_FILE_SIZE + 10000,
        max_size_bytes=FileSizeLimit.FILESIZE_UPLOAD,
    )


def random_voice_note():
    """
    Fixture to provide random voice note data.

    It provides what Telegram considers a voice note, ensuring that the file is small enough
    to be considered a voice note instead of a regular audio file.
    """
    return random_audio_generator(
        output_format=random.choice(["mp3", "m4a"]),
        max_size_bytes=FileSizeLimit.VOICE_NOTE_FILE_SIZE,
    )
