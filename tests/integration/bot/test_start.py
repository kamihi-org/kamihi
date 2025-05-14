"""
TODO: one-line module description.

TODO: Additional details about the module, its purpose, and any necessary
background information. Explain what functions or classes are included.

License:
    MIT

Examples:
    [Examples of how to use the module/classes/functions]

Attributes:
    [List any relevant module-level attributes with types and descriptions]
"""

import pytest
from telethon.tl.custom import Conversation

from kamihi.bot import Bot


@pytest.mark.asyncio
async def test_start_command(
    tg_client, test_user_id, bot_username, run_bot, wait_for_log_entry, create_user, create_permission_for_user
):
    """
    Test the /start command of the bot.
    """

    def configure_bot(bot: Bot):
        @bot.action
        async def start():
            """
            Handle the /start command.
            """
            return "Welcome to Kamihi! I'm here to assist you. How can I help you today?"

        user = create_user(test_user_id, False)
        create_permission_for_user("start", user)

        return bot

    with run_bot(configure_bot):
        wait_for_log_entry("SUCCESS", "Started!")

        async with tg_client.conversation(bot_username, timeout=10, max_messages=10000) as conv:
            conv: Conversation

            await conv.send_message("/start")
            response = await conv.get_response()  # Welcome message
            assert response.text == "Welcome to Kamihi! I'm here to assist you. How can I help you today?"
