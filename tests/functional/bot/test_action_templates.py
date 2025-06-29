"""
Functional tests for using templates in actions.

License:
    MIT

"""

from textwrap import dedent

import pytest
from telethon.tl.custom import Conversation


@pytest.mark.asyncio
@pytest.mark.usefixtures("kamihi")
@pytest.mark.parametrize(
    "actions_folder",
    [
        {
            "actions/start/__init__.py": "".encode(),
            "actions/start/start.py": dedent("""\
                from jinja2 import Template
                from kamihi import bot
                
                
                @bot.action
                async def start(template: Template):
                    return template.render(name="John Doe")
            """).encode(),
            "actions/start/start.md.jinja": "Hello, {{ name }}!".encode(),
        }
    ],
)
async def test_action_templates_single(user_in_db, add_permission_for_user, chat: Conversation, actions_folder):
    """Test the action decorator without parentheses."""
    add_permission_for_user(user_in_db, "start")

    await chat.send_message("/start")
    response = await chat.get_response()

    assert response.text == f"Hello, John Doe!"
