"""
Main file of the CLI utility for the Kamihi framework.

License:
    MIT

"""

import typer

from .commands import action_app, init_app, run_app, user_app

app = typer.Typer()
app.add_typer(action_app, name="action")
app.add_typer(init_app, name="init")
app.add_typer(run_app, name="run")
app.add_typer(user_app, name="user")


@app.command()
def version() -> None:
    """Print the version of the Kamihi framework and exits."""
    from kamihi import __version__

    print(__version__)  # noqa: T201


if __name__ == "__main__":
    app()
