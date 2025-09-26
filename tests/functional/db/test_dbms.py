"""
Functional tests for the database module.

License:
    MIT

"""

import pytest
from pytest_docker_tools import container, fetch
from pytest_docker_tools.wrappers import Container
from pytest_lazy_fixtures import lf, lfc

from tests.functional.conftest import KamihiContainer


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
)


@pytest.mark.parametrize(
    "db_url,pyproject_extra_dependencies",
    [
        (
            lfc("postgresql+psycopg2://kamihi:kamihi@{ip}:5432/kamihi".format, ip=lf("postgres_container.ips.primary")),
            ["psycopg2-binary"],
        )
    ],
)
def test_db_postgresql(db_url, pyproject_extra_dependencies, kamihi: KamihiContainer):
    """
    Test the system when using a PostgreSQL database.

    If kamihi has correctly started, multiple database calls
    will already have been made, so no extra checks are necessary.
    """
    pass
