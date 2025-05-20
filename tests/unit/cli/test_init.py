"""
Unit tests for the Kamihi CLI init command.

License:
    MIT

"""

import os
from pathlib import Path

import pytest


@pytest.fixture
def temp_cwd(tmp_path):
    """Fixture to change the current working directory to a temporary path."""
    original_cwd = Path.cwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(original_cwd)


def test_init(local_cli, temp_cwd):
    """Test the init command of the CLI."""
    runner, app = local_cli

    result = runner.invoke(app, ["init", "example_project"])

    assert result.exit_code == 0
    assert os.path.exists("example_project")
    assert os.path.exists("example_project/kamihi.yml")
    assert os.path.exists("example_project/pyproject.toml")
    assert '[project]\nname = "example_project"' in open("example_project/pyproject.toml").read()


def test_init_no_name(local_cli, temp_cwd):
    """Test the init command of the CLI without a name."""
    runner, app = local_cli

    result = runner.invoke(app, ["init"])
    assert result.exit_code == 2
    assert "Missing argument 'NAME'." in result.output


def test_init_other_path(local_cli, tmp_path):
    """Test the init command of the CLI with a different path."""
    runner, app = local_cli

    result = runner.invoke(app, ["init", "example_project", "--path", str(tmp_path)])

    assert result.exit_code == 0
    assert os.path.exists(tmp_path / "example_project")
    assert os.path.exists(tmp_path / "example_project/kamihi.yml")
    assert os.path.exists(tmp_path / "example_project/pyproject.toml")
    assert '[project]\nname = "example_project"' in open(tmp_path / "example_project/pyproject.toml").read()


def test_init_nonexistent_path(local_cli, tmp_path):
    """Test the init command of the CLI with an invalid path."""
    runner, app = local_cli

    result = runner.invoke(app, ["init", "example_project", "--path", str(tmp_path / "invalid")])

    assert result.exit_code == 2
    assert "Invalid value for '--path':" in result.output


def test_init_path_is_file(local_cli, tmp_path):
    """Test the init command of the CLI with a file as path."""
    runner, app = local_cli

    (tmp_path / "example_file.txt").touch()

    result = runner.invoke(app, ["init", "example_project", "--path", str(tmp_path / "example_file.txt")])

    assert result.exit_code == 2
    assert "Invalid value for '--path':" in result.output


def test_init_description(local_cli, temp_cwd):
    """Test the init command of the CLI with a description."""
    runner, app = local_cli

    result = runner.invoke(app, ["init", "example_project", "--description", "Test project"])

    assert result.exit_code == 0
    assert os.path.exists("example_project")
    assert os.path.exists("example_project/kamihi.yml")
    assert os.path.exists("example_project/pyproject.toml")
    assert (
        '[project]\nname = "example_project"\nversion = "0.0.0"\ndescription = "Test project"'
        in open("example_project/pyproject.toml").read()
    )
