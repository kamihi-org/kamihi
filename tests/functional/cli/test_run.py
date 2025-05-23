"""
Functional tests for the CLI run command.

License:
    MIT

"""

import pytest


@pytest.mark.parametrize("run_command", ["kamihi run"])
def test_run(kamihi, wait_for_log):
    """Test the run command."""
    wait_for_log("SUCCESS", "Started!")
    files = kamihi.get_files("/app")
    assert files["kamihi.yml"] == b""
