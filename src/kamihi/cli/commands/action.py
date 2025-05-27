"""
Action-related commands for the Kamihi CLI.

License:
    MIT

"""

import typer
from copier import run_copy

app = typer.Typer()


@app.command()
def new(
    ctx: typer.Context,
    name: str = typer.Argument(..., help="Name of the new action."),
    description: str = typer.Option("", help="Description of the new action."),
) -> None:
    """Create a new action."""
    run_copy(
        "gh:kamihi-dev/kamihi-action-template",
        str(ctx.obj.project),
        data={
            "action_name": name,
            "action_description": description,
        },
    )
