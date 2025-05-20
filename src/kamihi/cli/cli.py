"""
Main file of the CLI utility for the Kamihi framework.

License:
    MIT

"""

from pathlib import Path

import typer

from .commands import action_app, init_app, run_app, user_app, version_app

app = typer.Typer()
app.add_typer(version_app)
app.add_typer(init_app)
app.add_typer(action_app, name="action")
app.add_typer(run_app, name="run")
app.add_typer(user_app, name="user")


class Context:
    """
    Context for the Kamihi CLI utility.

    This class holds the context data for the CLI commands.
    """

    def __init__(self) -> None:
        """Initialize the context with default values."""
        self.cwd: Path = Path.cwd()
        self.templates: Path = Path(__file__).parent / "templates"
        self.project: Path = self.cwd


@app.callback()
def main(
    ctx: typer.Context,
) -> None:
    """
    Kamihi CLI utility.

    This utility provides commands to manage and interact with the Kamihi framework.
    """
    ctx.obj = Context()


if __name__ == "__main__":
    app()
