"""
Functional tests for the time type question.

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
            from datetime import time

            from kamihi import bot
            from kamihi.questions import Time

            @bot.action
            async def start(
                t: Annotated[time, Time(
                    text="Please provide a time.",
                    error_text="That doesn't seem like a valid time. Please try again.",
                    {question_args}
                )],
            ) -> str:
                return f"Your time is {{t.strftime('%H:%M:%S')}}."
        """,
    }


@pytest.mark.asyncio
async def test_base(user, add_permission_for_user, chat: Conversation):
    """Test the base functionality of the time question."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response = await chat.get_response()
    assert "Please provide a time." in response.text

    await chat.send_message("14:30")
    final_response = await chat.get_response()
    assert "Your time is 14:30:00." in final_response.text


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_input,expected_time",
    [
        ("14:30", "14:30:00"),
        ("2:30 pm", "14:30:00"),
        ("noon", "12:00:00"),
        ("midnight", "00:00:00"),
        ("07:05:09", "07:05:09"),
    ],
)
async def test_parsing_variations(
    user,
    add_permission_for_user,
    chat: Conversation,
    user_input,
    expected_time,
):
    """Test that various time formats (including natural language) are accepted."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    _ = await chat.get_response()

    await chat.send_message(user_input)
    final_response = await chat.get_response()
    assert f"Your time is {expected_time}." in final_response.text

