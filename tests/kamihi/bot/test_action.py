"""
Tests for the Action class in kamihi.bot.action.

License:
    MIT

"""

from __future__ import annotations

import inspect
from inspect import Signature, Parameter
from unittest.mock import MagicMock, Mock, patch, create_autospec, AsyncMock

import loguru
from loguru import logger
import pytest
from logot import Logot, logged
from telegram import Update
from telegram.constants import BotCommandLimit
from telegram.ext import ApplicationHandlerStop, CallbackContext, CommandHandler

from kamihi.bot.action import Action
from tests.kamihi.conftest import mock_update, mock_context


async def func():
    pass


@pytest.fixture
def action() -> Action:
    """Fixture for Action class."""
    return Action(name="test_action", commands=["test"], description="Test action", func=func)


def test_action_init(logot: Logot, action: Action) -> None:
    """Test the Action class initialization."""
    logot.assert_logged(logged.debug("Successfully registered"))

    assert action.name == "test_action"
    assert action.commands == ["test"]
    assert action.description == "Test action"
    assert action.func is func


@pytest.mark.parametrize(
    "command",
    [
        "/test",
        "invalid command",
        "",
        "a" * (BotCommandLimit.MAX_COMMAND + 1),
        "TEST",
    ],
)
def test_action_init_invalid_commands(logot: Logot, command: str) -> None:
    """Test the Action class initialization with invalid commands."""
    action = Action(name="test_action", commands=[command], description="Test action", func=func)

    logot.assert_logged(logged.warning(f"Command '/{command}' was discarded%s"))
    logot.assert_logged(logged.warning(f"No valid commands were given"))
    logot.assert_logged(logged.warning(f"Failed to register"))

    assert action.name == "test_action"
    assert action.commands == []
    assert action.is_valid() is False


def test_action_init_duplicate_commands(logot: Logot) -> None:
    """Test the Action class initialization with duplicate commands."""
    action = Action(name="test_action", commands=["test", "test"], description="Test action", func=func)

    logot.assert_logged(logged.debug(f"Successfully registered"))

    assert action.name == "test_action"
    assert action.commands == ["test"]
    assert action.description == "Test action"
    assert action.func is func
    assert action.is_valid() is True


def test_action_init_sync_function(logot: Logot):
    """Test the Action class initialization with invalid function."""

    def test_func():
        pass

    action = Action(name="test_action", commands=["test"], description="Test action", func=test_func)

    logot.assert_logged(logged.warning(f"Function should be a coroutine%s"))
    logot.assert_logged(logged.warning(f"Failed to register"))

    assert action.name == "test_action"
    assert action.commands == ["test"]
    assert action.description == "Test action"
    assert action.func is test_func
    assert action.is_valid() is False


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "parameter, valid",
    [
        ("update", True),
        ("context", True),
        ("logger", True),
        ("invalid", False),
        ("aaaaaaaaaaaaaaaaa", False),
        ("a123", False),
    ],
)
def test_action_init_function_parameter_names(logot: Logot, parameter: str, valid: bool) -> None:
    """Test the Action class initialization with function signature."""
    mock_function = AsyncMock()
    mock_function.__signature__ = Signature([Parameter(name=parameter, kind=Parameter.POSITIONAL_OR_KEYWORD)])

    action = Action(name="test_action", commands=["test"], description="Test action", func=mock_function)

    if valid:
        logot.assert_logged(logged.debug("Successfully registered"))
        assert action.is_valid() is True
    else:
        logot.assert_logged(logged.warning(f"Invalid parameter '{parameter}' in function"))
        logot.assert_logged(logged.warning(f"Failed to register"))
        assert action.is_valid() is False


def test_action_handler(action: Action) -> None:
    """Test the Action class handler property."""
    assert action.handler is not None
    assert isinstance(action.handler, CommandHandler)
    assert list(action.handler.commands) == action.commands
    assert action.handler.callback == action.__call__


def test_action_invalid_handler(action: Action) -> None:
    """Test the Action class handler property with invalid handler."""
    action._valid = False

    assert action.handler is None


@pytest.mark.asyncio
async def test_action_call(logot: Logot, mock_update, mock_context) -> None:
    """Test the Action class call method."""
    mock_function = AsyncMock()
    mock_function.__signature__ = Signature([])
    mock_function.__name__ = "test_function"

    action = Action(name="test_action", commands=["test"], description="Test action", func=mock_function)

    logot.assert_logged(logged.debug("Successfully registered"))

    with pytest.raises(ApplicationHandlerStop):
        await action(mock_update, mock_context)
        assert mock_function.assert_called_once()


@pytest.mark.asyncio
async def test_action_call_update(logot: Logot, mock_update, mock_context) -> None:
    """Test the Action class call method with update parameter."""
    mock_function = AsyncMock()
    mock_function.__signature__ = Signature([Parameter("update", kind=Parameter.POSITIONAL_OR_KEYWORD)])
    mock_function.__name__ = "test_function"

    action = Action(name="test_action", commands=["test"], description="Test action", func=mock_function)

    logot.assert_logged(logged.debug("Successfully registered"))

    with pytest.raises(ApplicationHandlerStop):
        await action(mock_update, mock_context)
        assert mock_function.assert_called_once_with(update=mock_update)


@pytest.mark.asyncio
async def test_action_call_context(logot: Logot, mock_update, mock_context) -> None:
    """Test the Action class call method with context parameter."""
    mock_function = AsyncMock()
    mock_function.__signature__ = Signature([Parameter("context", kind=Parameter.POSITIONAL_OR_KEYWORD)])
    mock_function.__name__ = "test_function"

    action = Action(name="test_action", commands=["test"], description="Test action", func=mock_function)

    logot.assert_logged(logged.debug("Successfully registered"))

    with pytest.raises(ApplicationHandlerStop):
        await action(mock_update, mock_context)
        assert mock_function.assert_called_once_with(context=mock_context)


@pytest.mark.asyncio
async def test_action_call_logger(logot: Logot, mock_update, mock_context) -> None:
    """Test the Action class call method with logger parameter."""
    mock_function = AsyncMock()
    mock_function.__signature__ = Signature([Parameter("logger", kind=Parameter.POSITIONAL_OR_KEYWORD)])
    mock_function.__name__ = "test_function"

    action = Action(name="test_action", commands=["test"], description="Test action", func=mock_function)

    logot.assert_logged(logged.debug("Successfully registered"))

    with pytest.raises(ApplicationHandlerStop):
        await action(mock_update, mock_context)
        assert mock_function.assert_called_once_with(logger=action._logger)


@pytest.mark.asyncio
async def test_action_invalid_call(logot: Logot, action: Action, mock_update, mock_context) -> None:
    """Test the Action class call method when invalid."""
    action._valid = False
    await action(mock_update, mock_context)
    await logot.await_for(logged.warning("Not valid, skipping execution"))
