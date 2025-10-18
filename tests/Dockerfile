# This Dockerfile is used to build a Kamihi project environment for functional testing purposes.

# Use the Astral UV image with Python 3.12 and Debian Bookworm as the base image.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:a6419e8c52bf167e5d82e285573c2abb8cf24339da91976e2ea6827b99f2aaab

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
