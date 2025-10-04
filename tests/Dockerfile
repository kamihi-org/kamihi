# This Dockerfile is used to build a Kamihi project environment for functional testing purposes.

# Use the Astral UV image with Python 3.12 and Debian Bookworm as the base image.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:6a1dccb65090d8c8467bb1e3fe34004cc4ac32b30dac6b40c37a0e41fbf72da8

# Install system dependencies required for Kamihi.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libmagic1=1:5.44-3 \
    && rm -rf /var/lib/apt/lists/*

# Copy the current local version of Kamihi to the image.
COPY . /lib/kamihi

# Add environment variables for future dependencies installation.
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PATH="/app/.venv/bin:$PATH"

# Sets the working directory to /app.
WORKDIR /app
