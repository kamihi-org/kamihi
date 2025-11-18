from asyncio import sleep

import pytest
from telethon.tl.custom import Conversation, Message


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
                async def start(template: Template) -> bot.Pages:
                    return bot.Pages([i for i in range(50)], template)
            """,
            "start/start.md.jinja": """\
                Them numbers:
                {% for num in data %}
                - {{ num }}
                {% endfor %}
            """,
        },
    ],
)
async def test_pages(user, add_permission_for_user, chat: Conversation, actions_folder):
    """Test actions that return paginated messages."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response: Message = await chat.get_response()

    assert "Them numbers:" in response.text
    for i in range(5):
        assert f"\u2981 {i}" in response.text

    # Press the Page 2 button
    await response.click(1)

    # Get the edited message
    response: Message = await chat.get_edit()

    assert "Them numbers:" in response.text
    for i in range(5, 10):
        assert f"\u2981 {i}" in response.text


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
                from typing import Annotated
                             
                @bot.action
                async def start(template: Template, template_first_page: Annotated[Template, "first_page.md.jinja"]) -> bot.Pages:
                    return bot.Pages([i for i in range(50)], template, first_page_template=template_first_page)
            """,
            "start/start.md.jinja": """\
                Them numbers:
                {% for num in data %}
                - {{ num }}
                {% endfor %}
            """,
            "start/first_page.md.jinja": """\
                This is a wonderful list of them numbers. Use the buttons below to navigate.
            """,
        },
    ],
)
async def test_first_page(user, add_permission_for_user, chat: Conversation, actions_folder):
    """Test actions that return paginated messages with a first page."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response: Message = await chat.get_response()

    assert "This is a wonderful list of them numbers." in response.text

    # Press the Next button to go to the second page (which is the first data page)
    await response.click(1)

    # Get the edited message
    response: Message = await chat.get_edit()

    assert "Them numbers:" in response.text
    for i in range(5):
        assert f"\u2981 {i}" in response.text


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
                async def start(template: Template) -> bot.Pages:
                    return bot.Pages([i for i in range(50)], template)
            """,
            "start/start.md.jinja": """\
                Them numbers:
                {% for num in data %}
                - {{ num }}
                {% endfor %}
            """,
        },
    ],
)
@pytest.mark.parametrize(
    "config_file",
    [
        {
            "kamihi.yaml": """\
                db:
                    pages_expiration_days: 0.000001
            """,
        },
    ],
)
async def test_expired(user, add_permission_for_user, chat: Conversation, actions_folder, config_file):
    """Test actions that return paginated messages that have expired."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response: Message = await chat.get_response()

    assert "Them numbers:" in response.text
    for i in range(5):
        assert f"\u2981 {i}" in response.text

    await sleep(2)

    # Trigger expiration by going forward and back a page
    await response.click(1)

    # Get the edited message
    response: Message = await chat.get_edit()

    assert "This paginated message has expired" in response.text
