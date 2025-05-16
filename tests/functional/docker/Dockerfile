FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

COPY . /lib/kamihi

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

COPY tests/functional/docker/pyproject.toml pyproject.toml
RUN uv lock && \
    uv sync --no-install-project --no-dev
