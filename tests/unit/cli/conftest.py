"""
TODO: one-line module description.

TODO: Additional details about the module, its purpose, and any necessary
background information. Explain what functions or classes are included.

License:
    MIT

Examples:
    [Examples of how to use the module/classes/functions]

Attributes:
    [List any relevant module-level attributes with types and descriptions]
"""

import os
from pathlib import Path

import pytest
from typer.testing import CliRunner


@pytest.fixture(scope="session")
def run_command():
    from kamihi.cli import app

    os.environ["NO_COLOR"] = "1"
    runner = CliRunner()

    def _run_command(*command: str):
        """Run a command in the specified directory."""
        return runner.invoke(app, command, color=False)

    return _run_command


@pytest.fixture
def temp_cwd(tmp_path):
    """Fixture to change the current working directory to a temporary path."""
    original_cwd = Path.cwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(original_cwd)


@pytest.fixture
def tmp_project(temp_cwd, run_command):
    """Fixture to create a temporary project directory."""
    result = run_command("init", "example_project")

    assert result.exit_code == 0
    assert os.path.exists(temp_cwd / "example_project")

    os.chdir(temp_cwd / "example_project")

    yield temp_cwd / "example_project"
