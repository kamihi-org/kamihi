"""
Unit tests for the Kamihi CLI version command.

License:
    MIT

"""


def test_version(run_command):
    """Test the version command of the CLI."""
    from kamihi import __version__

    result = run_command("version")

    assert result.exit_code == 0
    assert result.stdout.strip() == __version__
