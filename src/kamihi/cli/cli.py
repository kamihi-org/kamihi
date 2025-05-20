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
app.add_typer(action_app, name="action")
app.add_typer(init_app, name="init")
app.add_typer(run_app, name="run")
app.add_typer(user_app, name="user")


data = {}


@app.callback()
def main() -> None:
    """
    Kamihi CLI utility.

    This utility provides commands to manage and interact with the Kamihi framework.
    """
    data["cwd"] = Path.cwd()


if __name__ == "__main__":
    app()
