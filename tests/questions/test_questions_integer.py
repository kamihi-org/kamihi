"""
Tests for the integer type questions module.

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
            from kamihi.questions import Integer

            @bot.action
            async def start(
                age: Annotated[int, Integer(
                    text="How old are you?",
                    error_text="That doesn't seem like a valid age. Please try again.",
                    {question_args}
                )],
            ) -> str:
                return f"Your age is {{age}}."
        """,
    }


@pytest.mark.asyncio
async def test_base(user, add_permission_for_user, chat: Conversation):
    """Test the base functionality of the integer question."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response = await chat.get_response()
    assert "How old are you?" in response.text

    await chat.send_message("25")
    final_response = await chat.get_response()
    assert "Your age is 25." in final_response.text


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "question_args,valid_input,invalid_input,expected_error",
    [
        ("le=100", "100", "101", "The provided integer must be less than or equal to 100."),
        ("ge=18", "18", "17", "The provided integer must be greater than or equal to 18."),
        ("lt=10", "9", "10", "The provided integer must be less than 10."),
        ("gt=0", "1", "0", "The provided integer must be greater than 0."),
        ("multiple_of=5", "10", "12", "The provided integer must be a multiple of 5."),
        ("", "42", "notanumber", "The provided response is not a valid integer."),
    ],
)
async def test_validation(
    user,
    add_permission_for_user,
    chat: Conversation,
    question_args,
    valid_input,
    invalid_input,
    expected_error,
):
    """Test validation of the integer question."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response = await chat.get_response()
    assert "How old are you?" in response.text

    # Send invalid input
    await chat.send_message(invalid_input)
    error_response = await chat.get_response()
    assert expected_error in error_response.text

    # Send valid input
    await chat.send_message(valid_input)
    final_response = await chat.get_response()
    assert f"Your age is {valid_input}." in final_response.text
