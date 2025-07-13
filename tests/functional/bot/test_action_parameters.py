"""
Functional tests for action parameter injections.

License:
    MIT

"""

import pytest
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
async def test_action_parameter_user(user_in_db, add_permission_for_user, chat: Conversation, actions_folder):
    """Test the action decorator without parentheses."""
    add_permission_for_user(user_in_db, "start")

    await chat.send_message("/start")
    response = await chat.get_response()

    assert response.text == f"Hello, user with ID {user_in_db['telegram_id']}!"


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
                from kamihi import bot, BaseUser
                from mongoengine import StringField
                 
                @bot.user_class
                class MyCustomUser(BaseUser):
                    name: str = StringField()
            """,
        }
    ],
)
@pytest.mark.parametrize("user_custom_data", [{"name": "John Doe"}])
async def test_action_parameter_user_custom(
    user_in_db,
    add_permission_for_user,
    chat: Conversation,
    actions_folder,
    models_folder,
    user_custom_data,
):
    """Test the action decorator without parentheses."""
    add_permission_for_user(user_in_db, "start")

    await chat.send_message("/start")
    response = await chat.get_response()

    assert response.text == f"Hello, {user_in_db['name']}!"


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
        "simple",
        "custom_template_name",
        "custom_arg_name",
        "custom_template_and_arg_name",
        "custom_template_and_arg_name_multiple",
    ],
)
async def test_action_parameter_template(
    user_in_db, add_permission_for_user, chat: Conversation, actions_folder, expected_response
):
    """Test the action decorator without parentheses."""
    add_permission_for_user(user_in_db, "start")

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
async def test_action_parameter_templates(user_in_db, add_permission_for_user, chat: Conversation, actions_folder):
    """Test the action decorator without parentheses."""
    add_permission_for_user(user_in_db, "start")

    await chat.send_message("/start")
    response = await chat.get_response()

    assert response.text == "Hello, John Doe! Bye, John Doe!"
