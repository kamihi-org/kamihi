"""
Version command for the Kamihi CLI.

License:
    MIT

"""

import typer

app = typer.Typer()


@app.command()
def version() -> None:
    """Print the version of the Kamihi framework and exits."""
    from kamihi import __version__

    print(__version__)  # noqa: T201
