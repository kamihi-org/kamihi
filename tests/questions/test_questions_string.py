"""
Functional tests for the string type question.

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
            from kamihi.questions import String
            
            @bot.action
            async def start(
                name: Annotated[str, String(
                    text="What is your name?", 
                    error_text="That doesn't seem like a valid name. Please try again.",
                    {question_args}
                )],
            ) -> str:
                return f"Hello, {{name}}!"
        """,
    }


@pytest.mark.asyncio
async def test_base(user, add_permission_for_user, chat: Conversation):
    """Test the base functionality of the string question."""
    add_permission_for_user(user["telegram_id"], "start")
    await chat.send_message("/start")
    response = await chat.get_response()
    assert "What is your name?" in response.text

    await chat.send_message("John Doe")
    final_response = await chat.get_response()
    assert "Hello, John Doe!" in final_response.text

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "question_args,valid_input,invalid_input",
    [
        ("pattern=r'^[A-Z]{1}[A-Za-z]+$'", "John", "john"),
        ("min_length=3", "Ana", "Al"),
        ("max_length=5", "Chris", "Christopher"),
    ],
)
async def test_validation(
    user,
    add_permission_for_user,
    chat: Conversation,
    question_args,
    valid_input,
    invalid_input,
):
    """Test validation of the string question."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response = await chat.get_response()
    assert "What is your name?" in response.text

    # Send invalid input
    await chat.send_message(invalid_input)
    error_response = await chat.get_response()
    assert "That doesn't seem like a valid name. Please try again." in error_response.text

    # Send valid input
    await chat.send_message(valid_input)
    final_response = await chat.get_response()
    assert f"Hello, {valid_input}!" in final_response.text
