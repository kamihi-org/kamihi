FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

COPY . /lib/kamihi

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

COPY tests/integration/docker/pyproject.toml pyproject.toml
RUN uv lock
RUN uv sync --no-install-project --no-dev
