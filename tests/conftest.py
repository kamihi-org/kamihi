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
from PIL import Image
from pydub import AudioSegment
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


def random_video_path() -> Path:
    """Fixture to provide a random video as bytes."""
    return random.choice(list(Path("tests/static/videos").glob("*.mp4")))


def random_audio(output_format: Literal["mp3", "m4a"] = "mp3") -> bytes:
    """
    Generates random audio data as bytes in MP3 or M4A format.

    Args:
        output_format (Literal["mp3", "m4a"]): The format of the output audio file.

    Returns:
        bytes: The generated audio data in the specified format.

    """
    sample_rate = 44100
    duration_ms = random.randint(1000, 20000)

    num_samples = int(sample_rate * (duration_ms / 1000))

    t = np.linspace(0, duration_ms / 1000, num_samples, endpoint=False)
    random_frequency = np.random.uniform(100, 1000)

    audio_data_float = np.random.normal(0, 0.4, num_samples) + 0.1 * np.sin(2 * np.pi * t * random_frequency)
    audio_data_float = audio_data_float / np.max(np.abs(audio_data_float)) * 0.9
    audio_data_int16 = (audio_data_float * 32767).astype(np.int16)

    # Create an AudioSegment from the numpy array
    audio_segment = AudioSegment(
        audio_data_int16.tobytes(),
        frame_rate=sample_rate,
        sample_width=audio_data_int16.dtype.itemsize,
        channels=1,
    )

    audio_bytes_io = io.BytesIO()

    if output_format == "m4a":
        output_format = "ipod"

    # Export to the desired format with a reasonable quality
    audio_segment.export(audio_bytes_io, format=output_format, parameters=["-q:a", "4"])

    return audio_bytes_io.getvalue()
