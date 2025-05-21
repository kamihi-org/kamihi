"""
Kamihi framework project execution.

License:
    MIT

"""

import importlib
import sys
from pathlib import Path

import typer
from loguru import logger

app = typer.Typer()


def import_actions(actions_dir: Path) -> None:
    """
    Import all Python files from a specified directory.

    Args:
        actions_dir (str): The path to the directory containing Python files.

    """
    if not actions_dir.is_dir():
        logger.critical("The 'actions' directory does not exist.")
        sys.exit(1)

    logger.trace(f"Scanning for actions in {actions_dir}")

    for action_dir in actions_dir.iterdir():
        action_dir: Path
        action_name = action_dir.name
        lg = logger.bind(action=action_name)

        if action_dir.is_dir() and action_dir.name != "__pycache__" and (action_dir / "__init__.py").exists():
            action_file = action_dir / f"{action_name}.py"

            if action_file.exists() and action_file.is_file():
                module_full_name = f"actions.{action_name}.{action_name}"

                spec = importlib.util.spec_from_file_location(module_full_name, str(action_file))
                if spec is None:
                    lg.error(f"Could not find spec")
                    continue

                module = importlib.util.module_from_spec(spec)

                sys.modules[module_full_name] = module

                with lg.catch(message="Error loading action module"):
                    spec.loader.exec_module(module)
            else:
                lg.error(f"Action directory found, but no '{action_name}.py' file exists.")
        elif action_dir.is_dir():
            lg.error(f"Action directory found, but no '__init__.py' file exists.")


@app.command()
def run(
    ctx: typer.Context,
) -> None:
    """
    Run the Kamihi framework.

    This command starts the Kamihi framework, allowing you to interact with it.
    """
    from kamihi import _init_bot

    bot = _init_bot()

    import_actions(ctx.obj.cwd / "actions")

    bot.start()
