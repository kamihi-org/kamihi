"""
Functional tests for the CLI db command.

License:
    MIT

"""
from typing import Generator

import pytest
from pytest_docker_tools.wrappers import Container

from tests.functional.conftest import KamihiContainer


@pytest.fixture
def kamihi(kamihi_container: KamihiContainer, request) -> Generator[Container, None, None]:
    """Fixture that ensures the Kamihi container is started and ready."""
    kamihi_container.uv_sync()

    yield kamihi_container

    try:
        if request.node.rep_call.failed:
            title = f" Kamihi container logs for {request.node.name} "
            print(f"\n{title:=^80}")
            for line in kamihi_container.logs():
                if jline := kamihi_container.parse_log_json(line):
                    print(jline["text"].strip())
                else:
                    print(line.strip())
    except AttributeError:
        title = f" Kamihi container logs for {request.node.name} "
        print(f"\n{title:=^80}")
        for line in kamihi_container.logs():
            if jline := kamihi_container.parse_log_json(line):
                print(jline["text"].strip())
            else:
                print(line.strip())


def test_db_migrate(kamihi: KamihiContainer):
    """Test the db migrate command."""
    kamihi.db_migrate()

    assert any(
        key.startswith("versions/") and key.endswith("_auto_migration.py")
        for key
        in kamihi.get_files("/app/migrations/versions")
    )
    assert kamihi.query_db("SELECT version_num FROM alembic_version;") == [] # No migrations applied yet


def test_db_upgrade(kamihi: KamihiContainer):
    """Test the db upgrade command."""
    kamihi.db_migrate()
    kamihi.db_upgrade()

    revisions = kamihi.query_db("SELECT version_num FROM alembic_version;")
    assert len(revisions) == 1
    assert f"versions/{revisions[0][0]}_auto_migration.py" in kamihi.get_files("/app/migrations/versions")

def test_db_downgrade(kamihi: KamihiContainer):
    """Test the db downgrade command."""
    kamihi.db_migrate()
    kamihi.db_upgrade()

    revisions = kamihi.query_db("SELECT version_num FROM alembic_version;")
    assert len(revisions) == 1
    assert f"versions/{revisions[0][0]}_auto_migration.py" in kamihi.get_files("/app/migrations/versions")

    kamihi.run_command_and_wait_for_log(
        "kamihi db downgrade",
        "Downgraded",
        "SUCCESS",
        {"revision": "-1"},
    )

    revisions = kamihi.query_db("SELECT version_num FROM alembic_version;")
    assert len(revisions) == 0

