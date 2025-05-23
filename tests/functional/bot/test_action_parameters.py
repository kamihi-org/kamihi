"""
Functional tests for action parameter injections.

License:
    MIT

"""

from textwrap import dedent

import pytest
from mongoengine import StringField
from pytest_docker_tools.wrappers import Container
from telethon.tl.custom import Conversation


class TestActionParametersUser:
    """Test action decorator on function with user parameter."""

    @pytest.fixture
    def actions_code(self):
        """Fixture to provide the user code for the bot."""
        return {
            "start/__init__.py": "".encode(),
            "start/start.py": dedent("""\
                from kamihi import bot
                             
                @bot.action
                async def start(user):
                    return f"Hello, user with ID {user.telegram_id}!"
            """).encode(),
            "start2/__init__.py": "".encode(),
            "start2/start2.py": dedent("""\
                from kamihi import bot
                
                @bot.action
                async def start2():
                    return "Hello! I'm not your friendly bot."
            """).encode(),
        }

    @pytest.mark.asyncio
    async def test_action_parameter_user(self, kamihi, user_in_db, add_permission_for_user, chat: Conversation):
        """Test the action decorator without parentheses."""
        add_permission_for_user(user_in_db, "start")

        await chat.send_message("/start")
        response = await chat.get_response()

        assert response.text == f"Hello, user with ID {user_in_db.telegram_id}!"


class TestActionParametersUserCustom:
    """Test action decorator on function with user parameter and custom user class."""

    @pytest.fixture
    def actions_code(self):
        """Fixture to provide the user code for the bot."""
        return {
            "start/__init__.py": "".encode(),
            "start/start.py": dedent("""\
                from kamihi import bot
                             
                @bot.action
                async def start(user):
                    return f"Hello, {user.name}!"
            """).encode(),
        }

    @pytest.fixture
    def models_code(self):
        """Fixture to provide the actions volume for the bot."""
        return {
            "user.py": dedent("""\
                from kamihi import bot, BaseUser
                from mongoengine import StringField
                 
                @bot.user_class
                class User(BaseUser):
                    name: str = StringField()
            """).encode(),
        }

    @pytest.fixture
    async def user_in_db(self, kamihi: Container, test_settings):
        """Fixture that creates a user in the MongoDB database."""
        from kamihi import BaseUser

        class User(BaseUser):
            name: str = StringField()

        user = User(
            telegram_id=test_settings.user_id,
            name="John Doe",
        ).save()

        yield user

        user.delete()

    @pytest.mark.asyncio
    async def test_action_parameter_user_custom(self, kamihi, user_in_db, add_permission_for_user, chat: Conversation):
        """Test the action decorator without parentheses."""
        add_permission_for_user(user_in_db, "start")

        await chat.send_message("/start")
        response = await chat.get_response()

        assert response.text == f"Hello, {user_in_db.name}!"
