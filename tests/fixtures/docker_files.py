"""
User files simulation to mount in the docker container for testing.

License:
    MIT

"""

from pathlib import Path
from textwrap import dedent

import pytest
import toml


@pytest.fixture
def pyproject_extra_dependencies() -> list[str]:
    """Fixture to provide the dependencies for the pyproject.toml file."""
    return []


@pytest.fixture
def pyproject(pyproject_extra_dependencies: list[str]) -> dict:
    """Fixture to provide the path to the pyproject.toml file."""
    data = {
        "project": {
            "name": "kftp",
            "version": "0.0.0",
            "description": "kftp",
            "requires-python": ">=3.12",
            "dependencies": ["kamihi"] + pyproject_extra_dependencies,
        },
        "tool": {
            "uv": {"sources": {"kamihi": {"path": "/lib/kamihi"}}},
            "alembic": {"script_location": "%(here)s/migrations"},
        },
    }
    return {"pyproject.toml": toml.dumps(data)}


@pytest.fixture
def config_file() -> dict:
    """Fixture to provide the path to the kamihi.yaml file."""
    return {"kamihi.yaml": ""}


@pytest.fixture
def actions_folder() -> dict:
    """Fixture to provide the path to the actions folder."""
    return {}


@pytest.fixture
def models_folder() -> dict:
    """Fixture to provide the path to the models folder."""
    return {
        "user.py": """\
            from kamihi import BaseUser
            
            class User(BaseUser):
                __table_args__ = {'extend_existing': True}
        """
    }


@pytest.fixture
def migrations_folder() -> dict:
    """Fixture to provide the path to the migrations folder."""
    return {
        "versions/__init__.py": "",
        "__init__.py": "",
        "env.py": Path("tests/utils/migrations/env.py").read_text(),
        "script.py.mako": Path("tests/utils/migrations/script.py.mako").read_text(),
    }


@pytest.fixture
def app_folder(pyproject, config_file, actions_folder, models_folder, migrations_folder) -> dict:
    """Fixture to provide the path to the app folder."""
    res = {}
    res.update({key: dedent(value) for key, value in pyproject.items()})
    res.update({key: dedent(value) for key, value in config_file.items()})
    res.update(
        {"actions/" + key: dedent(value) if isinstance(value, str) else value for key, value in actions_folder.items()}
    )
    res.update(
        {"models/" + key: dedent(value) if isinstance(value, str) else value for key, value in models_folder.items()}
    )
    res.update(
        {
            "migrations/" + key: dedent(value) if isinstance(value, str) else value
            for key, value in migrations_folder.items()
        }
    )
    res = {key: value.encode() if isinstance(value, str) else value for key, value in res.items()}
    return res
