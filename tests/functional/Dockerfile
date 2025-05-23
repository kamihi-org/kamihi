# This Dockerfile is used to build a Kamihi project environment for functional testing purposes.

# Use the Astral UV image with Python 3.12 and Debian Bookworm as the base image.
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Using copier, generate a project from the template.
RUN uvx copier copy gh:kamihi-dev/kamihi-project-template /app --data project_name=kftb --data project_description=kftb
WORKDIR /app

# Remove example files
RUN rm -rf /app/actions/start /app/actions/models/user.py /app/kamihi.yml

# Point the template to the local kamihi library
RUN echo '\n[tool.uv.sources]\nkamihi = { path = "/lib/kamihi" }' >> pyproject.toml

# Copy the current local version of Kamihi to the image.
COPY . /lib/kamihi

# Install the template project dependencies.
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

RUN uv sync --no-dev

ENV PATH="/app/.venv/bin:$PATH"
