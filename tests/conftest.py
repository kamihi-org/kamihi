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
    # Pre-computed valid (width, height) pairs for sum=10000 and aspect ratio <=20
    # This eliminates computation overhead and ensures fast, reliable generation
    valid_pairs = [
        (476, 9524), (500, 9500), (600, 9400), (700, 9300), (800, 9200),
        (900, 9100), (1000, 9000), (1200, 8800), (1500, 8500), (2000, 8000),
        (2500, 7500), (3000, 7000), (3500, 6500), (4000, 6000), (4500, 5500),
        (5000, 5000), (5500, 4500), (6000, 4000), (6500, 3500), (7000, 3000),
        (7500, 2500), (8000, 2000), (8500, 1500), (8800, 1200), (9000, 1000),
        (9100, 900), (9200, 800), (9300, 700), (9400, 600), (9500, 500), (9524, 476)
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


if __name__ == "__main__":
    import time
    
    def time_function(func, iterations=10):
        """Time a function over multiple iterations."""
        times = []
        for i in range(iterations):
            start = time.perf_counter()
            result = func()
            end = time.perf_counter()
            times.append(end - start)
            print(f"Iteration {i+1}: {times[-1]:.4f}s, size: {len(result)} bytes")
        
        avg_time = sum(times) / len(times)
        print(f"Average time: {avg_time:.4f}s")
        return avg_time
    
    print("Testing current random_image function with constant:")
    print(f"FileSizeLimit.PHOTOSIZE_UPLOAD = {FileSizeLimit.PHOTOSIZE_UPLOAD}")
    time_function(random_image, 5)
