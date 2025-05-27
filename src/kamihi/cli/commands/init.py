"""
Initialization of projects with Kamihi.

License:
    MIT

"""

from pathlib import Path
from typing import Annotated

import typer
from copier import run_copy

from kamihi import __version__ as kamihi_version

app = typer.Typer()


@app.command()
def init(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Name of the project."),
    path: Annotated[
        Path | None,
        typer.Option(
            exists=True,
            file_okay=False,
            dir_okay=True,
            writable=True,
            resolve_path=True,
            help="Path to the project directory.",
        ),
    ] = None,
    description: str = typer.Option(
        "Kamihi project",
        help="Description of the project.",
    ),
) -> None:
    """Initialize a new Kamihi project."""
    run_copy(
        "gh:kamihi-dev/kamihi-project-template",
        str((path or ctx.obj.project) / name),
        data={
            "project_name": name,
            "project_description": description,
            "kamihi_version": kamihi_version,
        },
    )
