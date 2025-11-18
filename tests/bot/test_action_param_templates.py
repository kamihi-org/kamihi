"""
Test the `templates` parameter in action function signatures.

License:
    MIT

"""

import pytest
from telethon.tl.custom import Conversation


@pytest.fixture
def actions_folder():
    return {
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


@pytest.mark.asyncio
@pytest.mark.usefixtures("kamihi")
async def test_templates(user, add_permission_for_user, chat: Conversation, actions_folder):
    """Test the action decorator without parentheses."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response = await chat.get_response()

    assert response.text == "Hello, John Doe! Bye, John Doe!"
