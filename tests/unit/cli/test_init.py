"""
Unit tests for the Kamihi CLI init command.

License:
    MIT

"""

import os


def test_init(run_command, temp_cwd):
    """Test the init command of the CLI."""
    result = run_command("init", "example_project")

    assert result.exit_code == 0
    assert os.path.exists("example_project")
    assert os.path.exists("example_project/kamihi.yml")
    assert os.path.exists("example_project/pyproject.toml")
    assert '[project]\nname = "example_project"' in open("example_project/pyproject.toml").read()


def test_init_no_name(run_command, temp_cwd):
    """Test the init command of the CLI without a name."""
    result = run_command("init")
    assert result.exit_code == 2
    assert "Missing argument 'NAME'." in result.output


def test_init_other_path(run_command, tmp_path):
    """Test the init command of the CLI with a different path."""
    result = run_command("init", "example_project", "--path", str(tmp_path))

    assert result.exit_code == 0
    assert os.path.exists(tmp_path / "example_project")
    assert os.path.exists(tmp_path / "example_project/kamihi.yml")
    assert os.path.exists(tmp_path / "example_project/pyproject.toml")
    assert '[project]\nname = "example_project"' in open(tmp_path / "example_project/pyproject.toml").read()


def test_init_nonexistent_path(run_command, tmp_path, remove_ansi):
    """Test the init command of the CLI with an invalid path."""
    result = run_command("init", "example_project", "--path", str(tmp_path / "invalid"))

    assert result.exit_code == 2
    assert "Invalid value for '--path'" in remove_ansi(result.output)


def test_init_path_is_file(run_command, tmp_path, remove_ansi):
    """Test the init command of the CLI with a file as path."""
    (tmp_path / "example_file.txt").touch()

    result = run_command("init", "example_project", "--path", str(tmp_path / "example_file.txt"))

    assert result.exit_code == 2
    assert "Invalid value for '--path':" in remove_ansi(result.output)


def test_init_description(run_command, temp_cwd):
    """Test the init command of the CLI with a description."""
    result = run_command("init", "example_project", "--description", "Test project")

    assert result.exit_code == 0
    assert os.path.exists("example_project")
    assert os.path.exists("example_project/kamihi.yml")
    assert os.path.exists("example_project/pyproject.toml")
    assert (
        '[project]\nname = "example_project"\nversion = "0.0.0"\ndescription = "Test project"'
        in open("example_project/pyproject.toml").read()
    )
