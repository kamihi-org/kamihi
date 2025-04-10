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

from loguru import logger
from telegram import Bot, Message
from telegram.error import TelegramError


async def send_text(
    bot: Bot,
    chat_id: int,
    text: str,
    reply_to_message_id: int = None,
) -> Message | None:
    """
    Send a text message to a chat.

    Args:
        bot (Bot): The Telegram Bot instance.
        chat_id (int): The ID of the chat to send the message to.
        text (str): The text of the message.
        reply_to_message_id (int, optional): The ID of the message to reply to. Defaults to None.

    Returns:
        dict: The response from the Telegram API.

    """
    lg = logger.bind(chat_id=chat_id, message=text)

    if reply_to_message_id is not None:
        lg = lg.bind(reply_to=reply_to_message_id)

    with lg.catch(exception=TelegramError, message="Failed to send message"):
        reply = await bot.send_message(
            chat_id,
            text,
            message_thread_id=reply_to_message_id,
        )
        lg.debug(f"Message sent", message=reply)
        return reply
