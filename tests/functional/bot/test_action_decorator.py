"""
Functional tests for the action decorator.

License:
    MIT

"""

from textwrap import dedent

import pytest
from telethon.tl.custom import Conversation


class TestActionDecoratorNoParentheses:
    """
    Test the action decorator without parentheses.
    """

    @pytest.fixture
    def user_code(self):
        """Fixture to provide the user code for the bot."""
        return {
            "main.py": dedent("""\
                              from kamihi import bot
                             
                              @bot.action
                              async def start():
                                  return "test"
                             
                              bot.start()
                              """).encode()
        }

    @pytest.mark.asyncio
    async def test_action_decorator_no_parentheses(
        self, kamihi, user_in_db, add_permission_for_user, chat: Conversation
    ):
        """Test the action decorator without parentheses."""
        add_permission_for_user(user_in_db, "start")

        await chat.send_message("/start")
        response = await chat.get_response()

        assert response.text == "test"
