"""
TODO: one-line module description.

TODO: Additional details about the module, its purpose, and any necessary
background information. Explain what functions or classes are included.

License:
    MIT

Examples:
    [Examples of how to use the module/classes/functions]

Attributes:
    [List any relevant module-level attributes with types and descriptions]
"""

import io

import numpy as np
import pytest
from PIL import Image


def random_image() -> bytes:
    """Fixture to provide a random JPEG image as bytes."""
    width, height = 1000, 1000
    for _ in range(1000):
        candidate_width = np.random.randint(1, 10000)
        candidate_height = np.random.randint(1, 10000)

        if any(
            [
                candidate_width + candidate_height < 10000,
                candidate_width + candidate_height > 10000,
                max(candidate_width, candidate_height) / min(candidate_width, candidate_height) > 20,
            ]
        ):
            continue

        width = candidate_width
        height = candidate_height
        break

    pixel_data = np.random.randint(0, 256, size=(height, width, 3), dtype=np.uint8)
    img = Image.fromarray(pixel_data, "RGB")
    img_bytes_io = io.BytesIO()
    img.save(img_bytes_io, format="JPEG", quality=85, optimize=True)

    file_size_bytes = img_bytes_io.tell()
    if not file_size_bytes <= 10 * 1024 * 1024:
        raise ValueError(f"Generated image size {file_size_bytes} bytes is not within the specified range.")

    return img_bytes_io.getvalue()
