"""
User files simulation to mount in the docker container for testing.

License:
    MIT

"""

from pathlib import Path
from textwrap import dedent

import pytest
import yaml


@pytest.fixture
def db_url() -> str:
    """Fixture to provide the database URL."""
    return "sqlite:///./kamihi.db"


@pytest.fixture
def config_file(db_url) -> dict:
    """Fixture to provide the contents of the kamihi.yaml file."""
    return {"db": {"url": db_url}}


@pytest.fixture
def config_file_yml(config_file) -> dict:
    """Fixture to provide the contents of the kamihi.yaml file with DB URL."""
    return {"kamihi.yaml": yaml.dump(config_file)}


@pytest.fixture
def actions_folder() -> dict:
    """Fixture to provide the contents of the actions folder."""
    return {}


@pytest.fixture
def models_folder() -> dict:
    """Fixture to provide the contents of the models folder."""
    return {
        "user.py": """\
            from kamihi.db import BaseUser
            
            class User(BaseUser):
                __table_args__ = {'extend_existing': True}
        """
    }


@pytest.fixture
def questions_folder() -> dict:
    """Fixture to provide the contents of the questions folder."""
    return {}


@pytest.fixture
def migrations_folder() -> dict:
    """Fixture to provide the contents of the migrations folder."""
    return {
        "versions/__init__.py": "",
        "__init__.py": "",
        "env.py": Path("tests/utils/migrations/env.py").read_text(),
        "script.py.mako": Path("tests/utils/migrations/script.py.mako").read_text(),
    }


@pytest.fixture
def extra_files_bytes() -> dict[str, bytes]:
    """Fixture to provide the contents of extra files in bytes."""
    return {}


@pytest.fixture
def app_folder(
    config_file_yml, actions_folder, models_folder, questions_folder, migrations_folder, extra_files_bytes
) -> dict:
    """Fixture to provide the path to the app folder."""
    res = {}
    res.update({key: dedent(value) for key, value in config_file_yml.items()})
    res.update(
        {"actions/" + key: dedent(value) if isinstance(value, str) else value for key, value in actions_folder.items()}
    )
    res.update(
        {"models/" + key: dedent(value) if isinstance(value, str) else value for key, value in models_folder.items()}
    )
    res.update(
        {
            "questions/" + key: dedent(value) if isinstance(value, str) else value
            for key, value in questions_folder.items()
        }
    )
    res.update(
        {
            "migrations/" + key: dedent(value) if isinstance(value, str) else value
            for key, value in migrations_folder.items()
        }
    )
    res.update(extra_files_bytes)
    res = {key: value.encode() if isinstance(value, str) else value for key, value in res.items()}
    return res
