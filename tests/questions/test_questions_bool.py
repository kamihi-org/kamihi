"""
Tests for the bool type questions module.

License:
    MIT

"""

import pytest
from telethon.tl.custom import Conversation


@pytest.fixture
def question_args() -> str:
    """Fixture to provide extra question arguments as a string."""
    return ""


@pytest.fixture
def actions_folder(question_args) -> dict:
    return {
        "start/__init__.py": "",
        "start/start.py": f"""\
            from typing import Annotated

            from kamihi import bot
            from kamihi.questions import Bool

            @bot.action
            async def start(
                agree: Annotated[bool, Bool(
                    text="Do you agree?",
                    error_text="That doesn't seem like a valid boolean. Please try again.",
                    {question_args}
                )],
            ) -> str:
                return f"Your answer is {{agree}}."
        """,
    }


@pytest.mark.asyncio
async def test_base(user, add_permission_for_user, chat: Conversation):
    """Test the base functionality of the boolean question."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response = await chat.get_response()
    assert "Do you agree?" in response.text

    await chat.send_message("true")
    final_response = await chat.get_response()
    assert "Your answer is True." in final_response.text


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "question_args,valid_input,expected_bool,invalid_input",
    [
        ("true_values={'yes','y'}", "y", True, "maybe"),
        ("false_values={'no','n'}", "n", False, "perhaps"),
        ("true_values={'1'}, false_values={'0'}", "1", True, "2"),
        ("", "true", True, "idk"),
    ],
)
async def test_validation(
    user,
    add_permission_for_user,
    chat: Conversation,
    question_args,
    valid_input,
    expected_bool,
    invalid_input,
):
    """Test validation of the boolean question."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response = await chat.get_response()
    assert "Do you agree?" in response.text

    # Send invalid input
    await chat.send_message(invalid_input)
    error_response = await chat.get_response()
    assert "That doesn't seem like a valid boolean. Please try again." in error_response.text

    # Send valid input
    await chat.send_message(valid_input)
    final_response = await chat.get_response()
    assert f"Your answer is {expected_bool}." in final_response.text
