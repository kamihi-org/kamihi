"""
Tests for the Action class in kamihi.bot.action.

License:
    MIT

"""

from __future__ import annotations

from inspect import Signature, Parameter
from typing import Annotated
from unittest.mock import AsyncMock, Mock

import pytest
from jinja2 import Template, Environment, DictLoader
from logot import Logot, logged
from telegram.constants import BotCommandLimit
from telegram.ext import ApplicationHandlerStop, CommandHandler

from kamihi.bot.models import RegisteredAction
from kamihi.bot.action import Action
from kamihi.datasources import DataSource, DataSourceConfig
from kamihi.tg.handlers import AuthHandler
from kamihi.users import User


async def func():
    """Dummy function for Action class."""


@pytest.fixture
def mock_action_files() -> dict[str, str]:
    """Fixture for mock action files."""
    return {
        "test_action.md.jinja": "Test template content",
        "test_action.test.sql": "SELECT * FROM start",
    }


@pytest.fixture
def mock_jinja_env(mock_action_files):
    """Fixture for Jinja environment."""
    return Environment(loader=DictLoader(mock_action_files), autoescape=True)


@pytest.fixture
def mock_datasource():
    """Fixture for mock datasource."""

    def _mock_datasource(name: str = "test") -> DataSource:
        """Create a mock datasource."""
        ds = DataSource(DataSourceConfig(name=name))
        ds.fetch = AsyncMock()
        ds.fetch.return_value = [("test", "data")]
        return ds

    return _mock_datasource


@pytest.fixture
def action(monkeypatch, mock_jinja_env, mock_datasource) -> Action:
    """Fixture for Action class."""
    monkeypatch.setattr("kamihi.bot.action.Environment", lambda *a, **k: mock_jinja_env)
    action = Action(
        name="test_action",
        commands=["test"],
        description="Test action",
        func=func,
        datasources={"test": mock_datasource()},
    )
    return action


@pytest.fixture
def mock_function():
    """Fixture to construct a mock function."""

    def _mock_function(signature: Signature = Signature([])):
        """Create a mock function with a given signature."""
        mock_func = AsyncMock()
        mock_func.__signature__ = signature
        mock_func.__name__ = "mock_function"
        mock_func.__code__.co_filename = __file__
        return mock_func

    return _mock_function


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
        " ",
        "a" * (BotCommandLimit.MAX_COMMAND + 1),
        "TEST",
    ],
)
def test_action_init_invalid_commands(logot: Logot, command: str) -> None:
    """Test the Action class initialization with invalid commands."""
    with pytest.raises(ValueError, match="No valid commands were given"):
        Action(name="test_action", commands=[command], description="Test action", func=func)

    logot.assert_logged(logged.warning(f"Command '{command}' was discarded%s"))


def test_action_init_duplicate_commands(logot: Logot) -> None:
    """Test the Action class initialization with duplicate commands."""
    action = Action(name="test_action", commands=["test", "test"], description="Test action", func=func)

    logot.assert_logged(logged.debug("Successfully registered"))

    assert action.name == "test_action"
    assert action.commands == ["test"]
    assert action.description == "Test action"
    assert action._func is func


def test_action_init_sync_function(logot: Logot):
    """Test the Action class initialization with invalid function."""

    def test_func():
        raise NotImplementedError()

    with pytest.raises(ValueError, match="Function should be a coroutine"):
        Action(name="test_action", commands=["test"], description="Test action", func=test_func)


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
    mock_function.__code__.co_filename = __file__

    with pytest.raises(ValueError, match=r"Function parameters '\*args' and '\*\*kwargs' are not supported"):
        Action(name="test_action", commands=["test"], description="Test action", func=mock_function)


@pytest.mark.parametrize(
    "mock_action_files",
    [
        {
            "start.md.jinja": "Test template content",
            "start.not_test.sql": "SELECT * FROM test",
        },
    ],
)
def test_action_init_invalid_requests(logot: Logot, mock_action_files, action: Action) -> None:
    """Test the Action class initialization with invalid request files."""
    logot.assert_logged(logged.warning("Request file does not match any datasource, it will be ignored."))


def test_action_handler():
    """Test the Action class handler property."""
    action = Action(name="test_action", commands=["test"], description="Test action", func=func)

    assert isinstance(action.handler, AuthHandler)
    assert isinstance(action.handler.handler, CommandHandler)

    assert action.handler.name == "test_action"
    assert action.handler.handler.callback == action.__call__
    assert list(action.handler.handler.commands) == ["test"]


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


def test_action_param_template(
    logot: Logot, monkeypatch, mock_update, mock_context, mock_function, mock_jinja_env, mock_datasource
) -> None:
    """Test the Action class fill_parameters method with template parameter."""
    name = "template"
    param = Parameter(name, kind=Parameter.POSITIONAL_OR_KEYWORD)
    f = mock_function(Signature([param]))

    monkeypatch.setattr("kamihi.bot.action.Environment", lambda *a, **k: mock_jinja_env)
    action = Action(
        name="test_action",
        commands=["test"],
        description="Test action",
        func=f,
        datasources={"test": mock_datasource()},
    )

    logot.assert_logged(logged.debug("Successfully registered"))

    template = action._param_template(name, param)
    assert template.render() == "Test template content"


@pytest.mark.parametrize("mock_action_files", [{}])
def test_action_param_template_not_found(
    logot: Logot,
    monkeypatch,
    mock_update,
    mock_context,
    mock_function,
    mock_jinja_env,
    mock_datasource,
    mock_action_files,
) -> None:
    """Test the Action class _param_template method when template file is not found."""
    name = "template"
    param = Parameter(name, kind=Parameter.POSITIONAL_OR_KEYWORD)
    f = mock_function(Signature([param]))

    monkeypatch.setattr("kamihi.bot.action.Environment", lambda *a, **k: mock_jinja_env)
    action = Action(
        name="test_action",
        commands=["test"],
        description="Test action",
        func=f,
        datasources={"test": mock_datasource()},
    )

    logot.assert_logged(logged.debug("Successfully registered"))

    with pytest.raises(ValueError, match="No template found"):
        action._param_template(name, param)


def test_action_param_template_annotated(
    logot: Logot, monkeypatch, mock_update, mock_context, mock_function, mock_jinja_env, mock_datasource
) -> None:
    """Test the Action class fill_parameters method with annotated template parameter."""
    name = "template"
    param = Parameter(
        name, kind=Parameter.POSITIONAL_OR_KEYWORD, annotation=Annotated[Template, "test_action.md.jinja"]
    )
    f = mock_function(Signature([param]))

    monkeypatch.setattr("kamihi.bot.action.Environment", lambda *a, **k: mock_jinja_env)
    action = Action(
        name="test_action",
        commands=["test"],
        description="Test action",
        func=f,
        datasources={"test": mock_datasource()},
    )

    logot.assert_logged(logged.debug("Successfully registered"))

    template = action._param_template(name, param)
    assert template.render() == "Test template content"


def test_action_param_template_annotated_not_found(
    logot: Logot, monkeypatch, mock_update, mock_context, mock_function, mock_jinja_env, mock_datasource
) -> None:
    """Test the Action class _param_template method with annotated template parameter not found."""
    name = "template"
    param = Parameter(name, kind=Parameter.POSITIONAL_OR_KEYWORD, annotation=Annotated[Template, "not_found.md.jinja"])
    f = mock_function(Signature([param]))

    monkeypatch.setattr("kamihi.bot.action.Environment", lambda *a, **k: mock_jinja_env)
    action = Action(
        name="test_action",
        commands=["test"],
        description="Test action",
        func=f,
        datasources={"test": mock_datasource()},
    )

    logot.assert_logged(logged.debug("Successfully registered"))

    with pytest.raises(ValueError, match="No template found"):
        action._param_template(name, param)


@pytest.mark.parametrize(
    "annotation",
    [
        Annotated[Template, "invalid", "extra"],
        Annotated[Template, 123],
        Annotated["test_action.md.jinja", Template],
    ],
    ids=["extra_args", "invalid_type", "wrong_order"],
)
def test_action_param_template_annotated_invalid(
    logot: Logot, monkeypatch, mock_update, mock_context, mock_function, mock_jinja_env, mock_datasource, annotation
) -> None:
    """Test the Action class _param_template method with invalid annotated template parameter."""
    name = "template"
    param = Parameter(name, kind=Parameter.POSITIONAL_OR_KEYWORD, annotation=annotation)
    f = mock_function(Signature([param]))

    monkeypatch.setattr("kamihi.bot.action.Environment", lambda *a, **k: mock_jinja_env)
    action = Action(
        name="test_action",
        commands=["test"],
        description="Test action",
        func=f,
        datasources={"test": mock_datasource()},
    )

    logot.assert_logged(logged.debug("Successfully registered"))

    with pytest.raises(ValueError, match="Invalid Annotated arguments"):
        action._param_template(name, param)


@pytest.mark.asyncio
async def test_action_param_data(
    logot: Logot, monkeypatch, mock_update, mock_context, mock_function, mock_jinja_env, mock_datasource
) -> None:
    """Test the Action class fill_parameters method with data parameter."""
    name = "data"
    param = Parameter(name, kind=Parameter.POSITIONAL_OR_KEYWORD)
    f = mock_function(Signature([param]))

    monkeypatch.setattr("kamihi.bot.action.Environment", lambda *a, **k: mock_jinja_env)
    action = Action(
        name="test_action",
        commands=["test"],
        description="Test action",
        func=f,
        datasources={"test": mock_datasource()},
    )

    logot.assert_logged(logged.debug("Successfully registered"))

    data = await action._param_data(name, param)
    assert data == [("test", "data")]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mock_action_files",
    [
        {
            "test_action.md.jinja": "Test template content",
            "test_action.test.sql": "SELECT * FROM start",
            "test_action.test2.sql": "SELECT * FROM start",
        },
    ],
)
async def test_action_param_data_multiple_found(
    logot: Logot,
    monkeypatch,
    mock_update,
    mock_context,
    mock_function,
    mock_jinja_env,
    mock_datasource,
    mock_action_files,
) -> None:
    """Test the Action class _param_data method when multiple data sources are found."""
    name = "data"
    param = Parameter(name, kind=Parameter.POSITIONAL_OR_KEYWORD)
    f = mock_function(Signature([param]))

    monkeypatch.setattr("kamihi.bot.action.Environment", lambda *a, **k: mock_jinja_env)
    action = Action(
        name="test_action",
        commands=["test"],
        description="Test action",
        func=f,
        datasources={"test": mock_datasource(), "test2": mock_datasource("test2")},
    )

    logot.assert_logged(logged.debug("Successfully registered"))

    with pytest.raises(ValueError, match="Multiple requests found, specify one using annotated pattern"):
        await action._param_data(name, param)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mock_action_files",
    [
        {
            "test_action.md.jinja": "Test template content",
        },
    ],
)
async def test_action_param_data_not_found(
    logot: Logot,
    monkeypatch,
    mock_update,
    mock_context,
    mock_function,
    mock_jinja_env,
    mock_datasource,
    mock_action_files,
) -> None:
    """Test the Action class _param_data method when no data sources are found."""
    name = "data"
    param = Parameter(name, kind=Parameter.POSITIONAL_OR_KEYWORD)
    f = mock_function(Signature([param]))

    monkeypatch.setattr("kamihi.bot.action.Environment", lambda *a, **k: mock_jinja_env)
    action = Action(
        name="test_action",
        commands=["test"],
        description="Test action",
        func=f,
        datasources={"test": mock_datasource()},
    )

    logot.assert_logged(logged.debug("Successfully registered"))

    with pytest.raises(ValueError, match="Default request not found"):
        await action._param_data(name, param)


@pytest.mark.asyncio
async def test_action_param_data_annotated(
    logot: Logot, monkeypatch, mock_update, mock_context, mock_function, mock_jinja_env, mock_datasource
) -> None:
    """Test the Action class fill_parameters method with annotated data parameter."""
    name = "data"
    param = Parameter(name, kind=Parameter.POSITIONAL_OR_KEYWORD, annotation=Annotated[list, "test_action.test.sql"])
    f = mock_function(Signature([param]))

    monkeypatch.setattr("kamihi.bot.action.Environment", lambda *a, **k: mock_jinja_env)
    action = Action(
        name="test_action",
        commands=["test"],
        description="Test action",
        func=f,
        datasources={"test": mock_datasource()},
    )

    logot.assert_logged(logged.debug("Successfully registered"))

    data = await action._param_data(name, param)
    assert data == [("test", "data")]


@pytest.mark.asyncio
async def test_action_param_data_annotated_not_found(
    logot: Logot, monkeypatch, mock_update, mock_context, mock_function, mock_jinja_env, mock_datasource
) -> None:
    """Test the Action class _param_data method with annotated data parameter not found."""
    name = "data"
    param = Parameter(name, kind=Parameter.POSITIONAL_OR_KEYWORD, annotation=Annotated[list, "not_found.test.sql"])
    f = mock_function(Signature([param]))

    monkeypatch.setattr("kamihi.bot.action.Environment", lambda *a, **k: mock_jinja_env)
    action = Action(
        name="test_action",
        commands=["test"],
        description="Test action",
        func=f,
        datasources={"test": mock_datasource()},
    )

    logot.assert_logged(logged.debug("Successfully registered"))

    with pytest.raises(ValueError, match="Request file specified in annotation not found"):
        await action._param_data(name, param)


@pytest.mark.asyncio
async def test_action_param_data_annotated_custom_arg_name(
    logot: Logot, monkeypatch, mock_update, mock_context, mock_function, mock_jinja_env, mock_datasource
) -> None:
    """Test the Action class _param_data method with annotated data parameter with custom argument name."""
    name = "data_in"
    param = Parameter(name, kind=Parameter.POSITIONAL_OR_KEYWORD, annotation=Annotated[list, "test_action.test.sql"])
    f = mock_function(Signature([param]))

    monkeypatch.setattr("kamihi.bot.action.Environment", lambda *a, **k: mock_jinja_env)
    action = Action(
        name="test_action",
        commands=["test"],
        description="Test action",
        func=f,
        datasources={"test": mock_datasource()},
    )

    logot.assert_logged(logged.debug("Successfully registered"))

    data = await action._param_data(name, param)
    assert data == [("test", "data")]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "annotation",
    [
        Annotated[list, "invalid", "extra"],
        Annotated[list, 123],
        Annotated["test_action.test.sql", list],
    ],
    ids=["extra_args", "invalid_type", "wrong_order"],
)
async def test_action_param_data_annotated_invalid(
    logot: Logot, monkeypatch, mock_update, mock_context, mock_function, mock_jinja_env, mock_datasource, annotation
) -> None:
    """Test the Action class _param_data method with invalid annotated data parameter."""
    name = "data"
    param = Parameter(name, kind=Parameter.POSITIONAL_OR_KEYWORD, annotation=annotation)
    f = mock_function(Signature([param]))

    monkeypatch.setattr("kamihi.bot.action.Environment", lambda *a, **k: mock_jinja_env)
    action = Action(
        name="test_action",
        commands=["test"],
        description="Test action",
        func=f,
        datasources={"test": mock_datasource()},
    )

    logot.assert_logged(logged.debug("Successfully registered"))

    with pytest.raises(ValueError, match="Invalid Annotated arguments"):
        await action._param_data(name, param)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mock_action_files",
    [
        {
            "test_action.md.jinja": "Test template content",
            "in.test.sql": "SELECT * FROM start",
        }
    ],
)
async def test_action_param_data_custom_arg_name(
    logot: Logot,
    monkeypatch,
    mock_update,
    mock_context,
    mock_function,
    mock_jinja_env,
    mock_datasource,
    mock_action_files,
) -> None:
    """Test the Action class _param_data method with custom argument name."""
    name = "data_in"
    param = Parameter(name, kind=Parameter.POSITIONAL_OR_KEYWORD)
    f = mock_function(Signature([param]))

    monkeypatch.setattr("kamihi.bot.action.Environment", lambda *a, **k: mock_jinja_env)
    action = Action(
        name="test_action",
        commands=["test"],
        description="Test action",
        func=f,
        datasources={"test": mock_datasource()},
    )

    logot.assert_logged(logged.debug("Successfully registered"))

    data = await action._param_data(name, param)
    assert data == [("test", "data")]


@pytest.mark.asyncio
async def test_action_param_data_custom_arg_name_not_found(
    logot: Logot, monkeypatch, mock_update, mock_context, mock_function, mock_jinja_env, mock_datasource
) -> None:
    """Test the Action class _param_data method with custom argument name not found."""
    name = "data_in"
    param = Parameter(name, kind=Parameter.POSITIONAL_OR_KEYWORD)
    f = mock_function(Signature([param]))

    monkeypatch.setattr("kamihi.bot.action.Environment", lambda *a, **k: mock_jinja_env)
    action = Action(
        name="test_action",
        commands=["test"],
        description="Test action",
        func=f,
        datasources={"test": mock_datasource()},
    )

    logot.assert_logged(logged.debug("Successfully registered"))

    with pytest.raises(ValueError, match="No request found matching 'in'"):
        await action._param_data(name, param)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "mock_action_files",
    [
        {
            "test_action.md.jinja": "Test template content",
            "in.test.sql": "SELECT * FROM start",
            "in.test2.sql": "SELECT * FROM start",
        },
    ],
)
async def test_action_param_data_custom_arg_name_multiple_found(
    logot: Logot,
    monkeypatch,
    mock_update,
    mock_context,
    mock_function,
    mock_jinja_env,
    mock_datasource,
    mock_action_files,
) -> None:
    """Test the Action class _param_data method with custom argument name when multiple data sources are found."""
    name = "data_in"
    param = Parameter(name, kind=Parameter.POSITIONAL_OR_KEYWORD)
    f = mock_function(Signature([param]))

    monkeypatch.setattr("kamihi.bot.action.Environment", lambda *a, **k: mock_jinja_env)
    action = Action(
        name="test_action",
        commands=["test"],
        description="Test action",
        func=f,
        datasources={"test": mock_datasource(), "test2": mock_datasource("test2")},
    )

    logot.assert_logged(logged.debug("Successfully registered"))

    with pytest.raises(ValueError, match="Multiple requests matching 'in' found, specify one using annotated pattern"):
        await action._param_data(name, param)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "kind",
    [
        Parameter.POSITIONAL_OR_KEYWORD,
        Parameter.POSITIONAL_ONLY,
        Parameter.KEYWORD_ONLY,
    ],
)
async def test_action_fill_parameters_update(logot: Logot, mock_update, mock_context, kind, mock_function) -> None:
    """Test the Action class fill_parameters method with update parameter."""
    f = mock_function(Signature([Parameter("update", kind=kind)]))

    action = Action(name="test_action", commands=["test"], description="Test action", func=f)

    logot.assert_logged(logged.debug("Successfully registered"))

    pos_args, keyword_args = await action._fill_parameters(mock_update, mock_context)

    if kind == Parameter.POSITIONAL_ONLY:
        assert pos_args == [mock_update]
        assert keyword_args == {}
    else:
        assert pos_args == []
        assert keyword_args == {"update": mock_update}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "kind",
    [
        Parameter.POSITIONAL_OR_KEYWORD,
        Parameter.POSITIONAL_ONLY,
        Parameter.KEYWORD_ONLY,
    ],
)
async def test_action_fill_parameters_context(logot: Logot, mock_update, mock_context, kind, mock_function) -> None:
    """Test the Action class fill_parameters method with context parameter."""
    f = mock_function(Signature([Parameter("context", kind=kind)]))

    action = Action(name="test_action", commands=["test"], description="Test action", func=f)

    logot.assert_logged(logged.debug("Successfully registered"))

    pos_args, keyword_args = await action._fill_parameters(mock_update, mock_context)

    if kind == Parameter.POSITIONAL_ONLY:
        assert pos_args == [mock_context]
        assert keyword_args == {}
    else:
        assert pos_args == []
        assert keyword_args == {"context": mock_context}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "kind",
    [
        Parameter.POSITIONAL_OR_KEYWORD,
        Parameter.POSITIONAL_ONLY,
        Parameter.KEYWORD_ONLY,
    ],
)
async def test_action_fill_parameters_logger(logot: Logot, mock_update, mock_context, kind, mock_function) -> None:
    """Test the Action class fill_parameters method with logger parameter."""
    f = mock_function(Signature([Parameter("logger", kind=kind)]))

    action = Action(name="test_action", commands=["test"], description="Test action", func=f)

    logot.assert_logged(logged.debug("Successfully registered"))

    pos_args, keyword_args = await action._fill_parameters(mock_update, mock_context)

    if kind == Parameter.POSITIONAL_ONLY:
        assert pos_args == [action._logger]
        assert keyword_args == {}
    else:
        assert pos_args == []
        assert keyword_args == {"logger": action._logger}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "kind",
    [
        Parameter.POSITIONAL_OR_KEYWORD,
        Parameter.POSITIONAL_ONLY,
        Parameter.KEYWORD_ONLY,
    ],
)
async def test_action_fill_parameters_user(
    logot: Logot, monkeypatch, mock_update, mock_context, kind, mock_function
) -> None:
    """Test the Action class fill_parameters method with user parameter."""
    f = mock_function(Signature([Parameter("user", kind=kind)]))

    mock_user = User(telegram_id=123456789, is_admin=True)

    mock_get_user = Mock()
    mock_get_user.return_value = mock_user
    monkeypatch.setattr("kamihi.bot.action.get_user_from_telegram_id", mock_get_user)

    mock_update.effective_user.id = 123456789

    action = Action(name="test_action", commands=["test"], description="Test action", func=f)

    logot.assert_logged(logged.debug("Successfully registered"))

    pos_args, keyword_args = await action._fill_parameters(mock_update, mock_context)

    if kind == Parameter.POSITIONAL_ONLY:
        assert pos_args == [mock_user]
        assert keyword_args == {}
    else:
        assert pos_args == []
        assert keyword_args == {"user": mock_user}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "kind",
    [
        Parameter.POSITIONAL_OR_KEYWORD,
        Parameter.POSITIONAL_ONLY,
        Parameter.KEYWORD_ONLY,
    ],
)
async def test_action_fill_parameters_templates(
    logot: Logot, mock_update, mock_context, kind, mock_function, tmp_path
) -> None:
    """Test the Action class fill_parameters method with templates parameter."""
    f = mock_function(Signature([Parameter("templates", kind=kind)]))

    action = Action(name="test_action", commands=["test"], description="Test action", func=f)

    logot.assert_logged(logged.debug("Successfully registered"))

    pos_args, keyword_args = await action._fill_parameters(mock_update, mock_context)

    if kind == Parameter.POSITIONAL_ONLY:
        assert pos_args == [action._message_templates]
        assert keyword_args == {}
    else:
        assert pos_args == []
        assert keyword_args == {"templates": action._message_templates}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "kind",
    [
        Parameter.POSITIONAL_OR_KEYWORD,
        Parameter.POSITIONAL_ONLY,
        Parameter.KEYWORD_ONLY,
    ],
)
async def test_action_fill_parameters_template(
    logot: Logot, monkeypatch, mock_update, mock_context, kind, mock_function, tmp_path, mock_jinja_env
) -> None:
    """Test the Action class fill_parameters method with template parameter."""
    f = mock_function(Signature([Parameter("template", kind=kind)]))

    monkeypatch.setattr("kamihi.bot.action.Environment", lambda *a, **k: mock_jinja_env)
    action = Action(name="test_action", commands=["test"], description="Test action", func=f)

    logot.assert_logged(logged.debug("Successfully registered"))

    pos_args, keyword_args = await action._fill_parameters(mock_update, mock_context)

    if kind == Parameter.POSITIONAL_ONLY:
        assert pos_args == [mock_jinja_env.get_template("test_action.md.jinja")]
        assert keyword_args == {}
    else:
        assert pos_args == []
        assert keyword_args == {"template": mock_jinja_env.get_template("test_action.md.jinja")}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "kind",
    [
        Parameter.POSITIONAL_OR_KEYWORD,
        Parameter.POSITIONAL_ONLY,
        Parameter.KEYWORD_ONLY,
    ],
)
async def test_action_fill_parameters_data(
    logot: Logot, monkeypatch, mock_update, mock_context, kind, mock_function, mock_jinja_env, mock_datasource
) -> None:
    """Test the Action class fill_parameters method with data parameter."""
    f = mock_function(Signature([Parameter("data", kind=kind)]))

    monkeypatch.setattr("kamihi.bot.action.Environment", lambda *a, **k: mock_jinja_env)
    action = Action(
        name="test_action",
        commands=["test"],
        description="Test action",
        func=f,
        datasources={"test": mock_datasource()},
    )

    logot.assert_logged(logged.debug("Successfully registered"))

    pos_args, keyword_args = await action._fill_parameters(mock_update, mock_context)

    if kind == Parameter.POSITIONAL_ONLY:
        assert pos_args == [[("test", "data")]]
        assert keyword_args == {}
    else:
        assert pos_args == []
        assert keyword_args == {"data": [("test", "data")]}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "kind",
    [
        Parameter.POSITIONAL_OR_KEYWORD,
        Parameter.POSITIONAL_ONLY,
        Parameter.KEYWORD_ONLY,
    ],
)
@pytest.mark.parametrize(
    "mock_action_files",
    [
        {
            "test_action.md.jinja": "Test template content",
            "in.test.sql": "SELECT * FROM start",
        }
    ],
)
async def test_action_fill_parameters_data_custom_arg_name(
    logot: Logot,
    monkeypatch,
    mock_update,
    mock_context,
    kind,
    mock_function,
    mock_jinja_env,
    mock_datasource,
    mock_action_files,
) -> None:
    """Test the Action class fill_parameters method with data parameter with custom argument name."""
    f = mock_function(Signature([Parameter("data_in", kind=kind)]))

    monkeypatch.setattr("kamihi.bot.action.Environment", lambda *a, **k: mock_jinja_env)
    action = Action(
        name="test_action",
        commands=["test"],
        description="Test action",
        func=f,
        datasources={"test": mock_datasource()},
    )

    logot.assert_logged(logged.debug("Successfully registered"))

    pos_args, keyword_args = await action._fill_parameters(mock_update, mock_context)

    if kind == Parameter.POSITIONAL_ONLY:
        assert pos_args == [[("test", "data")]]
        assert keyword_args == {}
    else:
        assert pos_args == []
        assert keyword_args == {"data_in": [("test", "data")]}


@pytest.mark.asyncio
async def test_action_fill_parameters_invalid_parameter(logot: Logot, mock_update, mock_context, mock_function) -> None:
    """Test the Action class fill_parameters method with invalid parameter."""
    f = mock_function(Signature([Parameter("invalid", kind=Parameter.POSITIONAL_OR_KEYWORD)]))

    action = Action(name="test_action", commands=["test"], description="Test action", func=f)

    logot.assert_logged(logged.debug("Successfully registered"))

    await action._fill_parameters(mock_update, mock_context)

    logot.assert_logged(logged.warning("Failed to fill parameter, it will be set to None"))


@pytest.mark.asyncio
async def test_action_call(logot: Logot, mock_update, mock_context) -> None:
    """Test the Action class call method."""
    mock_function = AsyncMock()
    mock_function.__signature__ = Signature([])
    mock_function.__name__ = "test_function"
    mock_function.return_value = "test result"
    mock_function.__code__.co_filename = __file__

    action = Action(name="test_action", commands=["test"], description="Test action", func=mock_function)

    logot.assert_logged(logged.debug("Successfully registered"))

    with pytest.raises(ApplicationHandlerStop):
        await action(mock_update, mock_context)

    mock_function.assert_called_once()


def test_action_repr(action: Action) -> None:
    """Test the Action class string representation."""
    assert repr(action) == "Action 'test_action' (/test) [-> func]"
    assert str(action) == "Action 'test_action' (/test) [-> func]"
