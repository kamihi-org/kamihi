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


def import_file(path: Path, name: str) -> None:
    """
    Import a Python file from a specified path.

    Args:
        path (str): The path to the Python file.
        name (str): The name of the module.

    """
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None:
        logger.error(f"Could not find spec for {name}")
        return

    module = importlib.util.module_from_spec(spec)

    sys.modules[name] = module

    with logger.catch(message="Error loading module"):
        spec.loader.exec_module(module)


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
                lg.debug(f"Importing action from {action_file}")
                import_file(action_file, f"kamihi.actions.{action_name}")
            else:
                lg.error(f"Action directory found, but no '{action_name}.py' file exists.")
        elif action_dir.is_dir():
            lg.error(f"Action directory found, but no '__init__.py' file exists.")


def import_models(models_dir: Path) -> None:
    """
    Import all Python files from a specified directory.

    Args:
        models_dir (str): The path to the directory containing Python files.

    """
    if not models_dir.is_dir():
        logger.critical("The 'models' directory does not exist.")
        sys.exit(1)

    logger.trace(f"Scanning for models in {models_dir}")

    for model_file in models_dir.iterdir():
        model_file: Path
        model_name = model_file.stem
        lg = logger.bind(model=model_name)

        if model_file.is_file() and model_file.suffix == ".py":
            lg.trace(f"Importing model from {model_file}")
            import_file(model_file, f"kamihi.models.{model_name}")


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
    import_models(ctx.obj.cwd / "models")

    bot.start()
