"""
Tests for the Bot class in kamihi.bot.bot.

License:
    MIT

"""

from __future__ import annotations

import inspect

import pytest

from kamihi.base.config import KamihiSettings
from kamihi.bot.action import Action
from kamihi.bot.bot import Bot


@pytest.fixture
def mock_settings() -> KamihiSettings:
    """
    Fixture to provide a mock KamihiSettings instance.

    This fixture creates a mock instance of KamihiSettings for testing purposes.

    Returns:
        KamihiSettings: A mock instance of KamihiSettings.

    """
    return KamihiSettings()


@pytest.fixture(scope="function")
def mock_bot(mock_settings: KamihiSettings) -> Bot:
    """
    Fixture to provide a mock Bot instance.

    This fixture creates a mock instance of the Bot class for testing purposes.

    Args:
        mock_settings (KamihiSettings): The settings for the bot.

    Returns:
        Bot: A mock instance of the Bot class.

    """
    return Bot(mock_settings)


def test_bot_init(mock_settings: KamihiSettings) -> None:
    """
    Test the initialization of the Bot class.

    This test checks that the Bot class is initialized correctly with the given
    settings and that the templates are loaded properly.

    """
    bot = Bot(mock_settings)

    assert bot.settings == mock_settings
    assert bot._actions == []
    assert getattr(bot, "templates", None) is None


def test_bot_action_decorator_empty(mock_bot: Bot) -> None:
    """
    Test the bot action decorator with no parentheses.

    This test checks that the bot action decorator can be used without parentheses
    and that it correctly creates an Action instance.

    """

    @mock_bot.action
    async def dummy_action() -> None:
        pass

    assert isinstance(dummy_action, Action)
    assert dummy_action.name == "dummy_action"
    assert dummy_action.commands == ["dummy_action"]
    assert dummy_action.description is None
    assert "update" in inspect.signature(dummy_action).parameters
    assert "context" in inspect.signature(dummy_action).parameters


def test_bot_action_decorator_no_args(mock_bot: Bot) -> None:
    """
    Test the bot action decorator with no arguments.

    This test checks that the bot action decorator can be used without arguments
    and that it correctly creates an Action instance.

    """

    @mock_bot.action()
    async def dummy_action() -> None:
        pass

    assert isinstance(dummy_action, Action)
    assert dummy_action.name == "dummy_action"
    assert dummy_action.commands == ["dummy_action"]
    assert dummy_action.description is None
    assert "update" in inspect.signature(dummy_action).parameters
    assert "context" in inspect.signature(dummy_action).parameters


@pytest.mark.parametrize(
    "commands",
    [
        ["command1"],
        ["command1", "command2"],
        ["command1", "command2", "command3"],
    ],
)
def test_bot_action_decorator_commands(mock_bot: Bot, commands: list[str]) -> None:
    """
    Test the bot action decorator with commands.

    This test checks that the bot action decorator can be used with a list of
    commands and that it correctly creates an Action instance.

    Args:
        commands (list[str]): A list of command names.

    """

    @mock_bot.action(*commands)
    async def dummy_action() -> None:
        pass

    assert isinstance(dummy_action, Action)
    assert dummy_action.name == "dummy_action"
    assert sorted(dummy_action.commands) == sorted(commands)
    assert dummy_action.description is None
    assert "update" in inspect.signature(dummy_action).parameters
    assert "context" in inspect.signature(dummy_action).parameters


def test_bot_action_decorator_description(mock_bot: Bot) -> None:
    """
    Test the bot action decorator with a description.

    This test checks that the bot action decorator can be used with a description
    and that it correctly creates an Action instance.

    """

    @mock_bot.action(description="This is a test action")
    async def dummy_action() -> None:
        pass

    assert isinstance(dummy_action, Action)
    assert dummy_action.name == "dummy_action"
    assert dummy_action.commands == ["dummy_action"]
    assert dummy_action.description == "This is a test action"
    assert "update" in inspect.signature(dummy_action).parameters
    assert "context" in inspect.signature(dummy_action).parameters


def test_bot_action_function(mock_bot: Bot) -> None:
    """
    Test the bot action decorator as a function.

    This test checks that the bot action decorator can be used as a function
    and that it correctly creates an Action instance.

    """

    async def dummy_action() -> None:
        pass

    action = mock_bot.action("command1", "command2", description="This is a test action")(dummy_action)

    assert isinstance(action, Action)
    assert action.name == "dummy_action"
    assert sorted(action.commands) == sorted(["command1", "command2"])
    assert action.description == "This is a test action"
    assert "update" in inspect.signature(action).parameters
    assert "context" in inspect.signature(action).parameters
