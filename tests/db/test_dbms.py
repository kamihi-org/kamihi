"""
Functional tests for the database module.

License:
    MIT

"""

from typing import Any, Generator

import pytest
from pytest_docker_tools import container, fetch
from pytest_docker_tools.wrappers import Container
from pytest_lazy_fixtures import lf, lfc

from tests.fixtures.docker_container import KamihiContainer


def test_db_sqlite(kamihi: KamihiContainer):
    """
    Test the system when using a SQLite database.

    It is the default option, and if kamihi has correctly started,
    multiple database calls will already have been made, so checking
    if the file exists is sufficient.
    """
    assert kamihi.get_files("/app/kamihi.db") is not None


postgres_image = fetch(repository="postgres:latest")
"""Fixture that fetches the latest PostgreSQL image from Docker Hub."""


postgres_container = container(
    image="{postgres_image.id}",
    environment={"POSTGRES_USER": "kamihi", "POSTGRES_PASSWORD": "kamihi", "POSTGRES_DB": "kamihi"},
    network="{kamihi_network.name}",
)


@pytest.fixture
def postgres(postgres_container: Container) -> Generator[Container, Any, None]:
    """Fixture that provides the PostgreSQL container."""
    for log in postgres_container._container.logs(stream=True):
        if b"database system is ready to accept connections" in log:
            break
    yield postgres_container


@pytest.fixture
def kamihi(kamihi_container: KamihiContainer, postgres: Container) -> Generator[Container, None, None]:
    """Fixture that ensures the Kamihi container is started and ready with PostgreSQL."""
    kamihi_container.db_migrate()
    kamihi_container.db_upgrade()
    kamihi_container.start()

    yield kamihi_container

    kamihi_container.stop()


@pytest.mark.parametrize(
    "db_url",
    [
        lfc("postgresql+psycopg2://kamihi:kamihi@{ip}:5432/kamihi".format, ip=lf("postgres_container.ips.primary")),
    ],
)
def test_db_postgresql(db_url: str, kamihi: Container):
    """
    Test the system when using a PostgreSQL database.

    If kamihi has correctly started, multiple database calls
    will already have been made, so no extra checks are necessary.
    """
    pass
