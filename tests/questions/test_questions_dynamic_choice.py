"""
Functional tests for the dynamic choice type question.

License:
    MIT

"""

from pathlib import Path

import pytest
from telethon.tl.custom import Conversation


@pytest.fixture
def question_args() -> str:
    """Extra DynamicChoice arguments (e.g., reply_type, cols)."""
    return ""


@pytest.fixture
def actions_folder(question_args) -> dict:
    """Provide an action using DynamicChoice and a deterministic SQL request."""
    return {
        "start/__init__.py": "",
        "start/start.py": f"""\
            from typing import Annotated, Any
            from kamihi import bot
            from kamihi.questions import DynamicChoice

            @bot.action
            async def start(
                choice: Annotated[Any, DynamicChoice(
                    text="Pick an option:",
                    request="choices.sname.sql",
                    error_text="That doesn't seem like a valid choice. Please try again.",
                    {question_args}
                )],
            ) -> str:
                return f"Your choice is {{choice}}."
        """,
    }


@pytest.fixture
def questions_folder() -> dict:
    """Provide a SQL request file for DynamicChoice."""
    return {
        "choices.sname.sql": """\
            SELECT 'Yes' AS key, 'True' AS value
            UNION ALL SELECT 'No', 'False';
        """,
    }


@pytest.fixture
def config_file() -> dict:
    """Configure a local SQLite datasource named 'sname'."""
    return {
        "kamihi.yaml": """\
            datasources:
              - name: sname
                type: sqlite
                path: sample_sqlite.db
        """
    }


@pytest.fixture
def extra_files() -> dict:
    """Provide a sample SQLite database file."""
    return {
        "sample_sqlite.db": Path("tests/static/sample_data/sqlite.db").read_bytes(),
    }


@pytest.mark.asyncio
async def test_simple(user, add_permission_for_user, chat: Conversation):
    """Base flow with a dynamic choices request; simple reply."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response = await chat.get_response()
    assert "Pick an option:" in response.text

    await chat.send_message("Yes")
    final_response = await chat.get_response()
    assert "Your choice is True." in final_response.text


@pytest.mark.asyncio
async def test_validation(user, add_permission_for_user, chat: Conversation):
    """Invalid input yields error_text; valid input maps to the configured return value."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    _ = await chat.get_response()

    # Invalid input
    await chat.send_message("Maybe")
    error_response = await chat.get_response()
    assert "That doesn't seem like a valid choice. Please try again." in error_response.text

    # Valid input
    await chat.send_message("No")
    final_response = await chat.get_response()
    assert "Your choice is False." in final_response.text


@pytest.mark.asyncio
@pytest.mark.parametrize("question_args", ['reply_type="keyboard"'])
async def test_keyboard(user, add_permission_for_user, chat: Conversation, question_args):
    """Keyboard reply_type: handle transient 'Removing keyboard...' message deletion."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    prompt = await chat.get_response()
    assert "Pick an option:" in prompt.text

    await chat.send_message("Yes")
    first = await chat.get_response()
    if "Your choice is True." in first.text:
        final_response = first
    else:
        # Could be "Removing keyboard..." which might be deleted before we read it
        final_response = await chat.get_response()
    assert "Your choice is True." in final_response.text


@pytest.mark.asyncio
@pytest.mark.parametrize("question_args", ['reply_type="inline"'])
async def test_inline(user, add_permission_for_user, chat: Conversation, question_args):
    """Inline reply_type: click the inline button by its text."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response = await chat.get_response()
    assert "Pick an option:" in response.text

    # Find the "Yes" button and click it
    buttons = [btn for row in (response.buttons or []) for btn in row]
    try:
        yes_button = next(b for b in buttons if getattr(b, "text", "") == "Yes")
        await yes_button.click()
    except StopIteration:
        pytest.fail("Could not find 'Yes' button in inline keyboard.")

    final_response = await chat.get_response()
    assert "Your choice is True." in final_response.text
