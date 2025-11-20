"""
Functional tests for action parameter injections.

License:
    MIT

"""

from pathlib import Path

import pytest
from pytest_lazy_fixtures import lfc, lf
from telethon.tl.custom import Conversation


@pytest.mark.asyncio
@pytest.mark.usefixtures("kamihi")
@pytest.mark.parametrize(
    "actions_folder",
    [
        {
            "start/__init__.py": "",
            "start/start.py": """\
                from kamihi import bot
                             
                @bot.action
                async def start(user):
                    return f"Hello, user with ID {user.telegram_id}!"
            """,
        }
    ],
)
async def test_action_parameter_user(user, add_permission_for_user, chat: Conversation, actions_folder):
    """Test the action decorator without parentheses."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response = await chat.get_response()

    assert response.text == f"Hello, user with ID {user['telegram_id']}!"


@pytest.mark.asyncio
@pytest.mark.usefixtures("kamihi")
@pytest.mark.parametrize(
    "actions_folder",
    [
        {
            "start/__init__.py": "",
            "start/start.py": """\
                from kamihi import bot
                             
                @bot.action
                async def start(user):
                    return f"Hello, {user.name}!"
            """,
        }
    ],
)
@pytest.mark.parametrize(
    "models_folder",
    [
        {
            "user.py": """\
                from kamihi.db import BaseUser
                from sqlalchemy import Column, String
                
                class User(BaseUser):
                    __table_args__ = {'extend_existing': True}
                    name = Column(String, nullable=True)
            """,
        }
    ],
)
@pytest.mark.parametrize("user_custom_data", [{"name": "John Doe"}])
async def test_action_parameter_user_custom(
    user,
    add_permission_for_user,
    chat: Conversation,
    actions_folder,
    models_folder,
    user_custom_data,
):
    """Test the action decorator without parentheses."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response = await chat.get_response()

    assert response.text == f"Hello, {user['name']}!"


@pytest.mark.asyncio
@pytest.mark.usefixtures("kamihi")
@pytest.mark.parametrize(
    "actions_folder,expected_response",
    [
        (
            {
                "start/__init__.py": "",
                "start/start.py": """\
                    from jinja2 import Template
                    from kamihi import bot
                    
                    
                    @bot.action
                    async def start(template: Template):
                        return template.render(name="John Doe")
                """,
                "start/start.md.jinja": "Hello, {{ name }}!",
            },
            "Hello, John Doe!",
        ),
        (
            {
                "start/__init__.py": "",
                "start/start.py": """\
                    from jinja2 import Template
                    from kamihi import bot
                    from typing import Annotated
                    
                    @bot.action
                    async def start(template: Annotated[Template, "custom_template_name.md.jinja"]):
                        return template.render(name="John Doe")
                """,
                "start/custom_template_name.md.jinja": "Hello, {{ name }}!",
            },
            "Hello, John Doe!",
        ),
        (
            {
                "start/__init__.py": "",
                "start/start.py": """\
                    from jinja2 import Template
                    from kamihi import bot
                    
                    @bot.action
                    async def start(template_custom: Template):
                        return template_custom.render(name="John Doe")
                """,
                "start/start.md.jinja": "Hello, {{ name }}!",
            },
            "Hello, John Doe!",
        ),
        (
            {
                "start/__init__.py": "",
                "start/start.py": """\
                    from jinja2 import Template
                    from kamihi import bot
                    from typing import Annotated
                    
                    @bot.action
                    async def start(template_custom: Annotated[Template, "custom_template_name.md.jinja"]):
                        return template_custom.render(name="John Doe")
                """,
                "start/custom_template_name.md.jinja": "Hello, {{ name }}!",
            },
            "Hello, John Doe!",
        ),
        (
            {
                "start/__init__.py": "",
                "start/start.py": """\
                    from jinja2 import Template
                    from kamihi import bot
                    from typing import Annotated
                    
                    @bot.action
                    async def start(
                        template_hello: Annotated[Template, "hello.md.jinja"],
                        template_bye: Annotated[Template, "bye.md.jinja"]
                    ):
                        return template_hello.render(name="John Doe") + " " + template_bye.render(name="John Doe")
                """,
                "start/hello.md.jinja": "Hello, {{ name }}!",
                "start/bye.md.jinja": "Bye, {{ name }}!",
            },
            "Hello, John Doe! Bye, John Doe!",
        ),
    ],
    ids=[
        "implicit",
        "explicit",
        "custom_arg_name",
        "explicit_custom_arg_name",
        "explicit_multiple",
    ],
)
async def test_action_parameter_template(
    user, add_permission_for_user, chat: Conversation, actions_folder, expected_response
):
    """Test the action decorator without parentheses."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response = await chat.get_response()

    assert response.text == expected_response


@pytest.mark.asyncio
@pytest.mark.usefixtures("kamihi")
@pytest.mark.parametrize(
    "actions_folder",
    [
        {
            "start/__init__.py": "",
            "start/start.py": """\
                from jinja2 import Template
                from kamihi import bot
                
                @bot.action
                async def start(templates: dict[str, Template]):
                    return templates["start.md.jinja"].render(name="John Doe") + " " + templates["start2.md.jinja"].render(name="John Doe")
            """,
            "start/start.md.jinja": "Hello, {{ name }}!",
            "start/start2.md.jinja": "Bye, {{ name }}!",
        }
    ],
)
async def test_action_parameter_templates(user, add_permission_for_user, chat: Conversation, actions_folder):
    """Test the action decorator without parentheses."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response = await chat.get_response()

    assert response.text == "Hello, John Doe! Bye, John Doe!"


@pytest.mark.asyncio
@pytest.mark.usefixtures("kamihi")
@pytest.mark.usefixtures("sample_postgres_container")
@pytest.mark.parametrize(
    "config_file",
    [
        (
            {
                "kamihi.yaml": lfc(
                    """\
                        datasources:
                          - name: dname
                            type: postgresql
                            host: {host}
                            port: 5432
                            database: test_db
                            user: test_user
                            password: {password}
                    """.format,
                    host=lf("sample_postgres_container.ips.primary"),
                    password=lf("sample_postgres_password"),
                ),
            }
        )
    ],
)
@pytest.mark.parametrize(
    "actions_folder,expected_response",
    [
        (
            {
                "start/__init__.py": "",
                "start/start.py": """\
                    from kamihi import bot
                    
                    @bot.action
                    async def start(data: list):
                        return data[0].name
                """,
                "start/start.dname.sql": """\
                    SELECT * FROM lego_sets WHERE set_num = '00-1';
                """,
            },
            "Weetabix Castle",
        ),
        (
            {
                "start/__init__.py": "",
                "start/start.py": """\
                    from kamihi import bot
                    from typing import Annotated
    
                    @bot.action
                    async def start(data: Annotated[list, "request.dname.sql"]):
                        return data[0].name
                """,
                "start/request.dname.sql": """\
                    SELECT * FROM lego_sets WHERE set_num = '00-1';
                """,
            },
            "Weetabix Castle",
        ),
        (
            {
                "start/__init__.py": "",
                "start/start.py": """\
                    from kamihi import bot
                    
                    @bot.action
                    async def start(data_in: list):
                        return data_in[0].name
                """,
                "start/in.dname.sql": """\
                    SELECT * FROM lego_sets WHERE set_num = '00-1';
                """,
            },
            "Weetabix Castle",
        ),
        (
            {
                "start/__init__.py": "",
                "start/start.py": """\
                    from kamihi import bot
                    from typing import Annotated
    
                    @bot.action
                    async def start(data_in: Annotated[list, "request.dname.sql"]):
                        return data_in[0].name
                """,
                "start/request.dname.sql": """\
                    SELECT * FROM lego_sets WHERE set_num = '00-1';
                """,
            },
            "Weetabix Castle",
        ),
        (
            {
                "start/__init__.py": "",
                "start/start.py": """\
                    from kamihi import bot
                    from typing import Annotated
                    from jinja2 import Template
    
                    @bot.action
                    async def start(data_themes: list, data_colors: list, template: Template):
                        return template.render(
                            data_themes=data_themes,
                            data_colors=data_colors
                        )
                """,
                "start/themes.dname.sql": """\
                    SELECT * FROM lego_themes;
                """,
                "start/colors.dname.sql": """\
                    SELECT * FROM lego_colors;
                """,
                "start/start.md.jinja": """\
                    Themes: {{ data_themes | length }}
                    Colors: {{ data_colors | length }}
                """,
            },
            "Themes: 614\nColors: 135",
        ),
    ],
    ids=[
        "simple",
        "explicit",
        "custom_arg_name",
        "explicit_custom_arg_name",
        "multiple_custom_arg_name",
    ],
)
async def test_action_parameter_data(
    actions_folder, config_file, expected_response, user, add_permission_for_user, chat: Conversation
):
    """Test the "data" action parameter with SQL queries."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response = await chat.get_response()

    assert response.text == expected_response


@pytest.mark.asyncio
@pytest.mark.usefixtures("kamihi")
@pytest.mark.usefixtures("sample_postgres_container")
@pytest.mark.parametrize(
    "actions_folder,config_file,extra_files_bytes,expected_response",
    [
        (
            {
                "start/__init__.py": "",
                "start/start.py": """\
                    from kamihi import bot
                    
                    @bot.action
                    async def start(data_set: list, data_actor: list):
                        return f"{data_actor[0].first_name} {data_actor[0].last_name} bought one set of Legos called {data_set[0].name}"
                """,
                "start/set.lego.sql": """\
                    SELECT * FROM lego_sets WHERE set_num = '00-1';
                """,
                "start/actor.sakila.sql": """\
                    SELECT * FROM actor LIMIT 1;
                """,
            },
            {
                "kamihi.yaml": lfc(
                    """\
                        datasources:
                          - name: lego
                            type: postgresql
                            host: {host}
                            port: 5432
                            database: test_db
                            user: test_user
                            password: {password}
                          - name: sakila
                            type: sqlite
                            path: sample_sqlite.db
                    """.format,
                    host=lf("sample_postgres_container.ips.primary"),
                    password=lf("sample_postgres_password"),
                ),
            },
            {
                "sample_sqlite.db": Path("tests/static/sample_data/sqlite.db").read_bytes(),
            },
            "PENELOPE GUINESS bought one set of Legos called Weetabix Castle",
        ),
    ],
)
async def test_action_parameter_multiple_datasources(
    actions_folder, config_file, extra_files_bytes, expected_response, user, add_permission_for_user, chat: Conversation
):
    """Test the "data" action parameter with multiple datasources."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response = await chat.get_response()

    assert response.text == expected_response
