"""
Tests for the Bot class in kamihi.bot.bot.

License:
    MIT

"""

from __future__ import annotations

import inspect

import pytest
from logot import Logot, logged

from kamihi.base.config import KamihiSettings
from kamihi.bot.action import Action
from kamihi.bot.bot import Bot
from kamihi.datasources import SQLiteDataSourceConfig, SQLiteDataSource
from kamihi.tg.handlers import AuthHandler
from kamihi.users.models import User, Permission


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


def test_bot_init(mock_settings: KamihiSettings, mock_bot: Bot) -> None:
    """
    Test the initialization of the Bot class.

    This test checks that the Bot class is initialized correctly with the given
    settings and that the templates are loaded properly.

    """
    assert mock_bot.settings == mock_settings
    assert mock_bot._actions == []
    assert mock_bot.datasources == {}


def test_bot_init_with_datasource(mock_settings: KamihiSettings) -> None:
    """
    Test the initialization of the Bot class with a datasource.

    This test checks that the Bot class can be initialized with a datasource and that
    the datasource is correctly added to the bot's datasources.

    Args:
        mock_settings (KamihiSettings): The settings for the bot.

    """
    mock_settings.datasources.append(SQLiteDataSourceConfig(type="sqlite", name="mock", path="mock.db"))
    bot = Bot(mock_settings)

    assert "mock" in bot.datasources
    assert isinstance(bot.datasources["mock"], SQLiteDataSource)


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


def test_bot_action_decorator_error(mock_bot: Bot, logot: Logot) -> None:
    """
    Test the bot action decorator with an error.

    This test checks that the bot action decorator raises a ValueError if the
    action cannot be created.

    """

    @mock_bot.action
    def invalid_action() -> None:
        pass

    logot.assert_logged(logged.error("Failed to register action"))
    assert callable(invalid_action)


def test_bot_user_class(mock_bot: Bot) -> None:
    """
    Test the user_class method of the Bot class.

    This test checks that the user_class method sets the user model correctly.

    Args:
        mock_bot (Bot): The mock instance of the Bot class.

    """

    @mock_bot.user_class
    class MockUser(User):
        pass

    assert User.get_model() == MockUser


def test_bot_handlers(mock_bot: Bot) -> None:
    """
    Test the _handlers property of the Bot class.

    This test checks that the _handlers property returns the correct list of handlers.

    Args:
        mock_bot (Bot): The mock instance of the Bot class.

    """

    @mock_bot.action
    async def test_action() -> None:
        pass

    assert type(mock_bot._handlers[-1]) is AuthHandler
    assert mock_bot._handlers[-1].name == "test_action"


def test_bot_scopes(mock_bot: Bot) -> None:
    """
    Test the _scopes property of the Bot class.

    This test checks that the _scopes property returns the correct scopes for users.

    Args:
        mock_bot (Bot): The mock instance of the Bot class.

    """

    @mock_bot.action
    async def test_action() -> None:
        pass

    user = User(telegram_id=123456789)
    user = user.save()
    permission = Permission(action=mock_bot._actions[-1]._db_object, users=[user])
    permission.save()

    scopes = mock_bot._scopes
    assert 123456789 in scopes
    assert scopes[123456789][0].command == "test_action"
