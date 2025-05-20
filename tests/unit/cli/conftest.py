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

import pytest
from typer.testing import CliRunner


@pytest.fixture
def local_cli():
    from kamihi.cli import app

    runner = CliRunner()

    yield runner, app
