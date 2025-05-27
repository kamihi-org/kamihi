"""
Unit tests for the Kamihi CLI action command.

License:
    MIT

"""

import os


def test_action_new(run_command, tmp_project):
    """Test the action command of the CLI."""
    result = run_command("action", "new", "example_action")

    assert result.exit_code == 0
    assert os.path.exists("actions/example_action")
    assert os.path.exists("actions/example_action/example_action.py")
    assert os.path.exists("actions/example_action/__init__.py")


def test_action_new_no_name(run_command, tmp_project):
    """Test the action command of the CLI without a name."""
    result = run_command("action", "new")

    assert result.exit_code == 2
    assert "Missing argument 'NAME'." in result.output


def test_action_new_description(run_command, tmp_project):
    """Test the action command of the CLI with a description."""
    result = run_command("action", "new", "example_action", "--description", "This is an example action.")

    assert result.exit_code == 0
    assert os.path.exists("actions/example_action")
    assert os.path.exists("actions/example_action/example_action.py")
    assert os.path.exists("actions/example_action/__init__.py")

    with open("actions/example_action/example_action.py") as f:
        content = f.read()
        assert '@bot.action(description="This is an example action.")' in content
        assert "This is an example action." in content


def test_action_new_no_description(run_command, tmp_project):
    """Test the action command of the CLI without a description."""
    result = run_command("action", "new", "example_action")

    assert result.exit_code == 0
    assert os.path.exists("actions/example_action")
    assert os.path.exists("actions/example_action/example_action.py")
    assert os.path.exists("actions/example_action/__init__.py")

    with open("actions/example_action/example_action.py") as f:
        content = f.read()
        assert "@bot.action\n" in content
        assert '"""\n    example_action action.\n    \n    Returns:' in content
