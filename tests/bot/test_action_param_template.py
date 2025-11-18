"""
Test the `template` parameter in action function signatures.

License:
    MIT

"""
import pytest
from telethon.tl.custom import Conversation


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
async def test_template(
    user, add_permission_for_user, chat: Conversation, actions_folder, expected_response
):
    """Test the action decorator without parentheses."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response = await chat.get_response()

    assert response.text == expected_response
