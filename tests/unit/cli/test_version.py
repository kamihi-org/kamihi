"""
Functional tests for the Kamihi CLI version command.

License:
    MIT

"""


def test_version(local_cli):
    """Test the version command of the CLI."""
    runner, app = local_cli
    from kamihi import __version__

    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.stdout.strip() == __version__
