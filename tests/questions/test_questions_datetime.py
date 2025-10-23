"""
Functional tests for the datetime type question.

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
            from datetime import datetime

            from kamihi import bot
            from kamihi.questions import Datetime

            @bot.action
            async def start(
                dt: Annotated[datetime, Datetime(
                    text="Please provide a date and time.",
                    error_text="That doesn't seem like a valid date. Please try again.",
                    {question_args}
                )],
            ) -> str:
                return f"Your date is {{dt.isoformat()}}."
        """,
    }


@pytest.mark.asyncio
async def test_base(user, add_permission_for_user, chat: Conversation):
    """Test the base functionality of the datetime question with a full datetime."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response = await chat.get_response()
    assert "Please provide a date and time." in response.text

    await chat.send_message("2020-01-01 12:34")
    final_response = await chat.get_response()
    assert "Your date is 2020-01-01T12:34:00" in final_response.text


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "question_args,valid_input,expected_contains,invalid_input",
    [
        (
            "before=datetime(2020, 1, 1, 0, 0)",
            "2019-12-31 23:59",
            "2019-12-31T23:59:00",
            "2020-01-01 00:00",
        ),
        (
            "after=datetime(2020, 1, 1, 0, 0)",
            "2020-01-01 00:01",
            "2020-01-01T00:01:00",
            "2020-01-01 00:00",
        ),
        (
            "in_the_past=True",
            "2000-01-01 00:00",
            "2000-01-01T00:00:00",
            "2999-01-01 00:00",
        ),
        (
            "in_the_future=True",
            "2999-01-01 00:00",
            "2999-01-01T00:00:00",
            "2000-01-01 00:00",
        ),
        (
            "after=datetime(2019, 1, 1, 0, 0)",
            "January 1st, 2020 12:34",
            "2020-01-01T12:34:00",
            "January 1st, 2018 12:34",
        ),
    ],
)
async def test_validation(
    user,
    add_permission_for_user,
    chat: Conversation,
    question_args,
    valid_input,
    expected_contains,
    invalid_input,
):
    """Test validation of the datetime question with constraints and natural language."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response = await chat.get_response()
    assert "Please provide a date and time." in response.text

    # Send invalid (but parseable) input to trigger constraint errors
    await chat.send_message(invalid_input)
    error_response = await chat.get_response()
    assert "That doesn't seem like a valid date. Please try again." in error_response.text

    # Send valid input
    await chat.send_message(valid_input)
    final_response = await chat.get_response()
    assert expected_contains in final_response.text

