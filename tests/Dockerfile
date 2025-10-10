# This Dockerfile is used to build a Kamihi project environment for functional testing purposes.

# Use the Astral UV image with Python 3.12 and Debian Bookworm as the base image.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim@sha256:ba24faa296dff74a70e284a1ec7b27ec3bb86ecd5679c8a68550cd99e62f4a2b

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
