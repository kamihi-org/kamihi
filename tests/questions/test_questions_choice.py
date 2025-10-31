"""
Functional tests for the choice type question.

License:
    MIT

"""

import pytest
from telethon.tl.custom import Conversation


@pytest.fixture
def question_args() -> str:
    """Extra question arguments (e.g., reply_type)."""
    return ""


@pytest.fixture
def choices_expr() -> str:
    """The expression used for the 'choices' argument in the action file."""
    return "choices={'Yes': True, 'No': False}"


@pytest.fixture
def actions_folder(question_args, choices_expr) -> dict:
    return {
        "start/__init__.py": "",
        "start/start.py": f"""\
            from typing import Annotated, Any

            from kamihi import bot
            from kamihi.questions import Choice

            def get_choices():
                return {{
                    "A": "alpha",
                    "B": "beta",
                }}

            @bot.action
            async def start(
                choice: Annotated[Any, Choice(
                    text="Pick an option:",
                    {choices_expr},
                    error_text="That doesn't seem like a valid choice. Please try again.",
                    {question_args}
                )],
            ) -> str:
                return f"Your choice is {{choice}}."
        """,
    }


@pytest.mark.asyncio
async def test_simple(user, add_permission_for_user, chat: Conversation):
    """Base flow with a simple dict-based choices."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response = await chat.get_response()
    assert "Pick an option:" in response.text

    await chat.send_message("Yes")
    final_response = await chat.get_response()
    assert "Your choice is True." in final_response.text


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
    yes_button = next(b for b in buttons if getattr(b, "text", "") == "Yes")
    await yes_button.click()

    final_response = await chat.get_response()
    assert "Your choice is True." in final_response.text


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "choices_expr,question_args,valid_input,expected_value,invalid_input",
    [
        ("choices={'Yes': True, 'No': False}", "", "No", "False", "Maybe"),
        ("choices=['red', 'green']", "", "green", "green", "blue"),
        ("choices=[('One', 1), ('Two', 2)]", "", "Two", "2", "Three"),
        ("choices=get_choices()", "", "A", "alpha", "C"),
    ],
)
async def test_validation(
    user,
    add_permission_for_user,
    chat: Conversation,
    choices_expr,
    question_args,
    valid_input,
    expected_value,
    invalid_input,
):
    """Validation: wrong input yields error_text; valid input maps to the configured return value."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    _ = await chat.get_response()

    # Invalid input
    await chat.send_message(invalid_input)
    error_response = await chat.get_response()
    assert "That doesn't seem like a valid choice. Please try again." in error_response.text

    # Valid input
    await chat.send_message(valid_input)
    final_response = await chat.get_response()
    assert f"Your choice is {expected_value}." in final_response.text


# New tests for cols on keyboard and inline reply types


@pytest.mark.asyncio
@pytest.mark.parametrize("question_args", ['reply_type="keyboard", cols=2'])
@pytest.mark.parametrize("choices_expr", ["choices=['A','B','C','D','E']"])
async def test_keyboard_cols(user, add_permission_for_user, chat: Conversation, question_args, choices_expr):
    """Ensure keyboard layout respects cols=2 (rows: 2,2,1)."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response = await chat.get_response()
    assert "Pick an option:" in response.text

    rows = response.buttons or []
    texts_grid = [[getattr(btn, "text", "") for btn in row] for row in rows]
    flat = [t for row in texts_grid for t in row]
    assert flat == ["A", "B", "C", "D", "E"]
    assert len(rows) == 3
    assert len(rows[0]) == 2
    assert len(rows[1]) == 2
    assert len(rows[2]) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("question_args", ['reply_type="inline", cols=3'])
@pytest.mark.parametrize("choices_expr", ["choices=['A','B','C','D','E','F','G']"])
async def test_inline_cols(user, add_permission_for_user, chat: Conversation, question_args, choices_expr):
    """Ensure inline layout respects cols=3 (rows: 3,3,1)."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response = await chat.get_response()
    assert "Pick an option:" in response.text

    rows = response.buttons or []
    texts_grid = [[getattr(btn, "text", "") for btn in row] for row in rows]
    flat = [t for row in texts_grid for t in row]
    assert flat == ["A", "B", "C", "D", "E", "F", "G"]
    assert len(rows) == 3
    assert len(rows[0]) == 3
    assert len(rows[1]) == 3
    assert len(rows[2]) == 1
