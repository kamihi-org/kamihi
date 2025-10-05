"""
Utility functions for the Kamihi CLI.

License:
    MIT

"""

import importlib
import sys
import types
from pathlib import Path

import typer
from loguru import logger


def _ensure_namespace(pkg_name: str, path: Path, *aliases: str) -> None:
    """
    Ensure a namespace-like package exists in sys.modules.

    Ensure a namespace-like package exists in sys.modules pointing at `path`,
    and optionally create aliases that reference the same package module.
    """
    if pkg_name not in sys.modules:
        pkg = types.ModuleType(pkg_name)
        # Make it behave like a package searched at `path`
        pkg.__path__ = [str(path)]
        pkg.__package__ = pkg_name
        sys.modules[pkg_name] = pkg
    for alias in aliases:
        sys.modules[alias] = sys.modules[pkg_name]


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

    with logger.catch(message="Error importing file"):
        spec.loader.exec_module(module)


def import_actions(actions_dir: Path) -> None:
    """Import all Python files from a specified directory."""
    lg = logger.bind(actions_folder=str(actions_dir))
    if not actions_dir.is_dir():
        lg.warning("No actions directory found.")
        return

    _ensure_namespace("kamihi.actions", actions_dir, "actions")

    lg.trace("Scanning for actions")

    for action_dir in actions_dir.iterdir():
        action_dir: Path
        action_name = action_dir.name
        lg = logger.bind(action=action_name, folder=str(actions_dir))

        if action_dir.is_dir() and action_dir.name != "__pycache__" and (action_dir / "__init__.py").exists():
            action_file = action_dir / f"{action_name}.py"
            lg = lg.bind(file=str(action_file))

            if action_file.exists() and action_file.is_file():
                lg.debug("Importing action")
                import_file(action_file, f"kamihi.actions.{action_name}")

                sys.modules.setdefault(f"actions.{action_name}", sys.modules[f"kamihi.actions.{action_name}"])
            else:
                lg.error("Action directory found, but no '.py' file exists.")
        elif action_dir.is_dir():
            lg.error("Action directory found, but no '__init__.py' file exists.")


def import_models(models_dir: Path) -> None:
    """Import all Python files from a specified directory."""
    lg = logger.bind(folder=str(models_dir))
    if not models_dir.is_dir():
        lg.debug("No models directory found.")
        return

    _ensure_namespace("kamihi.models", models_dir, "models")

    lg.trace("Scanning for models")

    for model_file in models_dir.iterdir():
        model_file: Path
        model_name = model_file.stem
        lg = lg.bind(model=model_name)

        if model_file.is_file() and model_file.suffix == ".py":
            lg.bind(file=str(model_file)).trace("Importing model")
            import_file(model_file, f"kamihi.models.{model_name}")

            sys.modules.setdefault(f"models.{model_name}", sys.modules[f"kamihi.models.{model_name}"])


def telegram_id_callback(value: int | list[int]) -> int | list[int] | None:
    """
    Validate the Telegram ID.

    Args:
        value (int): The Telegram ID to validate.

    Returns:
        int: The validated Telegram ID.

    Raises:
        typer.BadParameter: If the Telegram ID is invalid.

    """
    if value is None:
        return value

    lvalue = [value] if not isinstance(value, list) else value

    for v in lvalue:
        if not isinstance(v, int) or v <= 0 or len(str(v)) > 16:
            msg = "Must be a positive integer with up to 16 digits"
            raise typer.BadParameter(msg)

    return value
