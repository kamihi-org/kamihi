"""
Tests for the Action class in kamihi.bot.action.

License:
    MIT

"""

from __future__ import annotations

from inspect import Signature, Parameter
from pathlib import Path
from typing import Any, Annotated
from unittest.mock import AsyncMock, patch

import pytest
from logot import Logot, logged
from telegram.constants import BotCommandLimit
from telegram.ext import ApplicationHandlerStop, CommandHandler
from typeguard import TypeCheckError

from kamihi.bot.models import RegisteredAction
from kamihi.bot.action import Action
from kamihi.bot.media import Document, Photo
from kamihi.tg.handlers import AuthHandler
from kamihi.users import User


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
    assert action._func is func


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
    logot.assert_logged(logged.warning("No valid commands were given"))
    logot.assert_logged(logged.warning("Failed to register"))

    assert action.name == "test_action"
    assert action.commands == []
    assert action.is_valid() is False


def test_action_init_duplicate_commands(logot: Logot) -> None:
    """Test the Action class initialization with duplicate commands."""
    action = Action(name="test_action", commands=["test", "test"], description="Test action", func=func)

    logot.assert_logged(logged.debug("Successfully registered"))

    assert action.name == "test_action"
    assert action.commands == ["test"]
    assert action.description == "Test action"
    assert action._func is func
    assert action.is_valid() is True


def test_action_init_sync_function(logot: Logot):
    """Test the Action class initialization with invalid function."""

    def test_func():
        raise NotImplementedError()

    action = Action(name="test_action", commands=["test"], description="Test action", func=test_func)

    logot.assert_logged(logged.warning("Function should be a coroutine%s"))
    logot.assert_logged(logged.warning("Failed to register"))

    assert action.name == "test_action"
    assert action.commands == ["test"]
    assert action.description == "Test action"
    assert action._func is test_func
    assert action.is_valid() is False


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
        logot.assert_logged(logged.warning("Failed to register"))
        assert action.is_valid() is False


@pytest.mark.parametrize(
    "parameter, kind",
    [
        ("args", Parameter.VAR_POSITIONAL),
        ("kwargs", Parameter.VAR_KEYWORD),
    ],
)
def test_action_init_function_varargs(logot: Logot, parameter, kind) -> None:
    """Test the Action class initialization with function signature."""
    mock_function = AsyncMock()
    mock_function.__signature__ = Signature([Parameter(name=parameter, kind=kind)])

    action = Action(name="test_action", commands=["test"], description="Test action", func=mock_function)

    logot.assert_logged(logged.warning("Special arguments '*args' and '**kwargs' are not supported%s"))
    logot.assert_logged(logged.warning("Failed to register"))

    assert action.is_valid() is False


def test_action_handler():
    """Test the Action class handler property."""
    action = Action(name="test_action", commands=["test"], description="Test action", func=func)

    assert isinstance(action.handler, AuthHandler)
    assert isinstance(action.handler.handler, CommandHandler)

    assert action.handler.name == "test_action"
    assert action.handler.handler.callback == action.__call__
    assert list(action.handler.handler.commands) == ["test"]


def test_action_handler_invalid():
    """Test the Action class handler property when invalid."""
    action = Action(name="test_action", commands=["test"], description="Test action", func=func)
    action._valid = False

    assert action.handler is None


def test_action_save_to_db():
    """Test the Action class save_to_db method on new action creation."""
    Action(name="test_action", commands=["test"], description="Test action", func=func)

    assert RegisteredAction.objects.count() == 1
    assert RegisteredAction.objects(name="test_action").first().name == "test_action"
    assert RegisteredAction.objects(name="test_action").first().description == "Test action"


def test_action_save_to_db_existing():
    """Test the Action class save_to_db method on existing action update."""
    Action(name="test_action", commands=["test"], description="Test action", func=func)
    Action(name="test_action", commands=["test"], description="Updated description", func=func)

    assert RegisteredAction.objects.count() == 1
    assert RegisteredAction.objects(name="test_action").first().description == "Updated description"


def test_action_clean_up():
    """Test the Action class clean_up method."""
    Action(name="test_action", commands=["test"], description="Test action", func=func)
    Action(name="test_action_2", commands=["test_2"], description="Test action 2", func=func)

    assert RegisteredAction.objects.count() == 2

    Action.clean_up(["test_action"])

    assert RegisteredAction.objects.count() == 1
    assert RegisteredAction.objects(name="test_action_2").first() is None


@pytest.mark.parametrize(
    "annotation, result",
    [
        (Signature.empty, "This is a test result"),
        (str, "This is a test result"),
    ],
)
def test_action_validate_result(logot: Logot, action: Action, annotation: type, result: Any) -> None:
    """Test the Action class validate_result method with valid result."""
    action._func = AsyncMock()
    action._func.__signature__ = Signature(return_annotation=annotation)

    assert action._validate_result(result)


@pytest.mark.parametrize(
    "annotation, result",
    [
        (str, 123456),
        (str, None),
    ],
)
def test_action_validate_result_invalid(logot: Logot, action: Action, annotation: type, result: Any) -> None:
    """Test the Action class validate_result method with invalid result."""
    action._func = AsyncMock()
    action._func.__signature__ = Signature(return_annotation=annotation)

    with pytest.raises(TypeCheckError):
        action._validate_result(result)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "result,signature,expected_call,expected_args,expected_kwargs",
    [
        ("Test string result", Signature.empty, "kamihi.bot.action.send_text", ["Test string result"], {}),
        ("Test string result", str, "kamihi.bot.action.send_text", ["Test string result"], {}),
        (Path("/test/doc.txt"), Signature.empty, "kamihi.bot.action.send_document", [Path("/test/doc.txt")], {}),
        (Path("/test/photo.jpg"), Signature.empty, "kamihi.bot.action.send_document", [Path("/test/photo.jpg")], {}),
        (
            Path("/test/doc.txt"),
            Annotated[Path, Document()],
            "kamihi.bot.action.send_document",
            [Path("/test/doc.txt")],
            {"caption": None},
        ),
        (
            Path("/test/photo.jpg"),
            Annotated[Path, Photo()],
            "kamihi.bot.action.send_photo",
            [Path("/test/photo.jpg")],
            {"caption": None},
        ),
        (
            Path("/test/doc.txt"),
            Annotated[Path, Document(caption="Test caption")],
            "kamihi.bot.action.send_document",
            [Path("/test/doc.txt")],
            {"caption": "Test caption"},
        ),
        (
            Path("/test/photo.jpg"),
            Annotated[Path, Photo(caption="Test caption")],
            "kamihi.bot.action.send_photo",
            [Path("/test/photo.jpg")],
            {"caption": "Test caption"},
        ),
        (
            Document(Path("/test/doc.pdf")),
            Signature.empty,
            "kamihi.bot.action.send_document",
            [Path("/test/doc.pdf")],
            {"caption": None},
        ),
        (
            Document(Path("/test/doc.pdf"), caption="Test document"),
            Document,
            "kamihi.bot.action.send_document",
            [Path("/test/doc.pdf")],
            {"caption": "Test document"},
        ),
        (
            Photo(Path("/test/photo.jpg")),
            Photo,
            "kamihi.bot.action.send_photo",
            [Path("/test/photo.jpg")],
            {"caption": None},
        ),
        (
            Photo(Path("/test/photo.jpg"), caption="Test photo"),
            Signature.empty,
            "kamihi.bot.action.send_photo",
            [Path("/test/photo.jpg")],
            {"caption": "Test photo"},
        ),
    ],
)
async def test_action_send_result(
    action: Action, mock_update, mock_context, result, expected_call, signature, expected_args, expected_kwargs
) -> None:
    action._func = AsyncMock()
    action._func.__signature__ = Signature(return_annotation=signature)

    with patch(expected_call) as mock_send:
        await action._send_result(result, mock_update, mock_context)

        mock_send.assert_called_once_with(*expected_args, mock_update, mock_context, **expected_kwargs)


@pytest.mark.asyncio
async def test_action_send_result_invalid(logot: Logot, action: Action, mock_update, mock_context) -> None:
    """Test _send_result with an invalid result."""
    action._func = AsyncMock()
    action._func.__signature__ = Signature(return_annotation=str)

    with pytest.raises(TypeError, match="Unexpected return type <class 'int'>"):
        await action._send_result(123456, mock_update, mock_context)


@pytest.mark.asyncio
async def test_action_send_result_none(logot: Logot, action: Action, mock_update, mock_context) -> None:
    """Test _send_result with None result."""
    action._func = AsyncMock()
    action._func.__signature__ = Signature(return_annotation=type(None))

    result = None

    with (
        patch("kamihi.bot.action.send_photo") as mock_send_photo,
        patch("kamihi.bot.action.send_document") as mock_send_document,
        patch("kamihi.bot.action.send_text") as mock_send_text,
    ):
        await action._send_result(result, mock_update, mock_context)

        logot.assert_logged(logged.debug("Function returned None, skipping reply"))
        mock_send_photo.assert_not_called()
        mock_send_document.assert_not_called()
        mock_send_text.assert_not_called()


@pytest.mark.asyncio
async def test_action_send_result_unexpected_type(action: Action, mock_update, mock_context) -> None:
    """Test _send_result with unexpected return type raises TypeError."""
    action._func = AsyncMock()
    action._func.__signature__ = Signature(return_annotation=Signature.empty)

    # Use an unexpected type that doesn't match any case
    result = 42  # int doesn't match any case

    with pytest.raises(TypeError, match=f"Unexpected return type {int}"):
        await action._send_result(result, mock_update, mock_context)


@pytest.mark.asyncio
async def test_action_send_list_result(logot: Logot, action: Action, mock_update, mock_context) -> None:
    """Test _send_result with a list of results."""
    action._func = AsyncMock()
    action._func.__signature__ = Signature(return_annotation=Signature.empty)

    results = ["First result", "Second result"]

    with patch("kamihi.bot.action.send_text") as mock_send_text:
        await action._send_result(results, mock_update, mock_context)

        assert mock_send_text.call_count == 2
        mock_send_text.assert_any_call("First result", mock_update, mock_context)
        mock_send_text.assert_any_call("Second result", mock_update, mock_context)


@pytest.mark.asyncio
async def test_action_call(logot: Logot, mock_update, mock_context) -> None:
    """Test the Action class call method."""
    mock_function = AsyncMock()
    mock_function.__signature__ = Signature([])
    mock_function.__name__ = "test_function"
    mock_function.return_value = "test result"

    action = Action(name="test_action", commands=["test"], description="Test action", func=mock_function)

    logot.assert_logged(logged.debug("Successfully registered"))

    with pytest.raises(ApplicationHandlerStop):
        await action(mock_update, mock_context)

    mock_function.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "kind",
    [
        Parameter.POSITIONAL_OR_KEYWORD,
        Parameter.POSITIONAL_ONLY,
        Parameter.KEYWORD_ONLY,
    ],
)
async def test_action_call_update(logot: Logot, mock_update, mock_context, kind) -> None:
    """Test the Action class call method with update parameter."""
    mock_function = AsyncMock()
    mock_function.__signature__ = Signature([Parameter("update", kind=kind)])
    mock_function.__name__ = "test_function"
    mock_function.return_value = "test result"

    action = Action(name="test_action", commands=["test"], description="Test action", func=mock_function)

    logot.assert_logged(logged.debug("Successfully registered"))

    with pytest.raises(ApplicationHandlerStop):
        await action(mock_update, mock_context)
        assert mock_function.assert_called_once_with(update=mock_update)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "kind",
    [
        Parameter.POSITIONAL_OR_KEYWORD,
        Parameter.POSITIONAL_ONLY,
        Parameter.KEYWORD_ONLY,
    ],
)
async def test_action_call_context(logot: Logot, mock_update, mock_context, kind) -> None:
    """Test the Action class call method with context parameter."""
    mock_function = AsyncMock()
    mock_function.__signature__ = Signature([Parameter("context", kind=kind)])
    mock_function.__name__ = "test_function"
    mock_function.return_value = "test result"

    action = Action(name="test_action", commands=["test"], description="Test action", func=mock_function)

    logot.assert_logged(logged.debug("Successfully registered"))

    with pytest.raises(ApplicationHandlerStop):
        await action(mock_update, mock_context)
        assert mock_function.assert_called_once_with(context=mock_context)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "kind",
    [
        Parameter.POSITIONAL_OR_KEYWORD,
        Parameter.POSITIONAL_ONLY,
        Parameter.KEYWORD_ONLY,
    ],
)
async def test_action_call_logger(logot: Logot, mock_update, mock_context, kind) -> None:
    """Test the Action class call method with logger parameter."""
    mock_function = AsyncMock()
    mock_function.__signature__ = Signature([Parameter("logger", kind=kind)])
    mock_function.__name__ = "test_function"
    mock_function.return_value = "test result"

    action = Action(name="test_action", commands=["test"], description="Test action", func=mock_function)

    logot.assert_logged(logged.debug("Successfully registered"))

    with pytest.raises(ApplicationHandlerStop):
        await action(mock_update, mock_context)
        assert mock_function.assert_called_once_with(logger=action._logger)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "kind",
    [
        Parameter.POSITIONAL_OR_KEYWORD,
        Parameter.POSITIONAL_ONLY,
        Parameter.KEYWORD_ONLY,
    ],
)
async def test_action_call_user(logot: Logot, mock_update, mock_context, kind) -> None:
    """Test the Action class call method with user parameter."""
    mock_function = AsyncMock()
    mock_function.__signature__ = Signature([Parameter("user", kind=kind)])
    mock_function.__name__ = "test_function"
    mock_function.return_value = "test result"

    mock_user = User(telegram_id=123456789, is_admin=True)

    mock_get_user = AsyncMock()
    mock_get_user.return_value = mock_user
    patch("kamihi.bot.action.get_user_from_telegram_id", mock_get_user)

    mock_update.effective_user.id = 123456789

    action = Action(name="test_action", commands=["test"], description="Test action", func=mock_function)

    logot.assert_logged(logged.debug("Successfully registered"))

    with pytest.raises(ApplicationHandlerStop):
        await action(mock_update, mock_context)
        assert mock_function.assert_called_once_with(user=mock_user)


@pytest.mark.asyncio
async def test_action_call_unknown_parameter(logot: Logot, mock_update, mock_context) -> None:
    """Test the Action class call method with an unknown parameter name."""
    # Create a mock function with an unknown parameter
    mock_function = AsyncMock()
    mock_function.__signature__ = Signature([Parameter("unknown", kind=Parameter.POSITIONAL_OR_KEYWORD)])
    mock_function.__name__ = "test_function"
    mock_function.return_value = "test result"

    # Bypass validation to create a valid action with an unknown parameter
    action = Action(name="test_action", commands=["test"], description="Test action", func=mock_function)
    action._valid = True  # Force action to be valid despite invalid parameter

    with pytest.raises(ApplicationHandlerStop):
        await action(mock_update, mock_context)
        mock_function.assert_called_once_with(unknown=None)  # Value should be None


@pytest.mark.asyncio
async def test_action_invalid_call(logot: Logot, action: Action, mock_update, mock_context) -> None:
    """Test the Action class call method when invalid."""
    action._valid = False
    await action(mock_update, mock_context)
    await logot.await_for(logged.warning("Not valid, skipping execution"))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "return_value",
    [
        "test result",
        None,
    ],
)
async def test_action_call_with_result(logot: Logot, action: Action, mock_update, mock_context, return_value) -> None:
    """Test the Action class call method with a result."""
    str_func = AsyncMock(return_value=return_value)
    action._func = str_func

    with pytest.raises(ApplicationHandlerStop):
        await action(mock_update, mock_context)
        str_func.assert_called_once_with(update=mock_update, context=mock_context)
        if return_value is None:
            logot.assert_logged(logged.debug("No result to send"))
        logot.assert_logged(logged.debug("Executed successfully"))


def test_action_repr(action: Action) -> None:
    """Test the Action class string representation."""
    assert repr(action) == "Action 'test_action' (/test) [-> func]"
    assert str(action) == "Action 'test_action' (/test) [-> func]"
