"""
Auxiliary Docker containers.

License:
    MIT

"""

import random
import string
from pathlib import Path

import pytest
from pytest_docker_tools import fetch, volume, container


@pytest.fixture(scope="session")
def sample_postgres_password() -> str:
    """
    Fixture that provides a sample PostgreSQL password.

    Returns:
        str: A randomly generated password for the sample PostgreSQL container.
    """
    return "".join(random.choices(string.ascii_letters + string.digits, k=32))


sample_postgres_image = fetch(repository="postgres:latest")
"""Fixture that fetches the sample PostgreSQL container image."""

sample_postgres_volume = volume(
    scope="session", initial_content={"lego.sql": Path("tests/static/sample_data/postgres.sql").read_bytes()}
)

sample_postgres_container = container(
    image="{sample_postgres_image.id}",
    environment={
        "POSTGRES_USER": "test_user",
        "POSTGRES_PASSWORD": "{sample_postgres_password}",
        "POSTGRES_DB": "test_db",
    },
    volumes={
        "{sample_postgres_volume.name}": {"bind": "/docker-entrypoint-initdb.d"},
    },
    scope="session",
)
