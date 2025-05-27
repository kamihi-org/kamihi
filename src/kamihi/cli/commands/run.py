"""
Kamihi framework project execution.

License:
    MIT

"""

import importlib
import sys
from pathlib import Path
from typing import Annotated

import typer
from loguru import logger
from validators import ValidationError, hostname

from kamihi import KamihiSettings, _init_bot
from kamihi.base.config import LogLevel

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
        logger.warning("No actions directory found.")
        return

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
            lg.error("Action directory found, but no '__init__.py' file exists.")


def import_models(models_dir: Path) -> None:
    """
    Import all Python files from a specified directory.

    Args:
        models_dir (str): The path to the directory containing Python files.

    Returns:
        bool: True if models were imported successfully, False otherwise.

    """
    if not models_dir.is_dir():
        logger.debug("No models directory found.")
        return

    logger.trace(f"Scanning for models in {models_dir}")

    for model_file in models_dir.iterdir():
        model_file: Path
        model_name = model_file.stem
        lg = logger.bind(model=model_name)

        if model_file.is_file() and model_file.suffix == ".py":
            lg.trace(f"Importing model from {model_file}")
            import_file(model_file, f"kamihi.models.{model_name}")


def host_callback(
    value: str | None,
) -> str | None:
    """
    Ensure the host value is valid.

    Args:
        value (str | None): The host value.

    Returns:
        str | None: The validated host value.

    """
    if value and isinstance(hostname(value, may_have_port=False), ValidationError):
        raise typer.BadParameter("Invalid host value")
    return value


@app.command()
def run(
    ctx: typer.Context,
    log_level: Annotated[
        LogLevel | None,
        typer.Option(
            "--log-level", "-l", help="Set the logging level for console loggers.", show_default=LogLevel.INFO
        ),
    ] = None,
    web_host: Annotated[
        str | None,
        typer.Option(
            ..., "--host", "-h", help="Host of the admin web panel", callback=host_callback, show_default="localhost"
        ),
    ] = None,
    web_port: Annotated[
        int | None,
        typer.Option(..., "--port", "-p", help="Port of the admin web panel", min=1024, max=65535, show_default="4242"),
    ] = None,
) -> None:
    """Run a project with the Kamihi framework."""
    settings = KamihiSettings.from_yaml(ctx.obj.config) if ctx.obj.config is not None else KamihiSettings()
    if web_host:
        settings.web.host = web_host
    if web_port:
        settings.web.port = web_port
    if log_level:
        settings.log.stdout_level = log_level
        settings.log.stderr_level = log_level
        settings.log.file_level = log_level
        settings.log.notification_level = log_level

    bot = _init_bot(settings)

    import_actions(ctx.obj.cwd / "actions")
    import_models(ctx.obj.cwd / "models")

    bot.start()
