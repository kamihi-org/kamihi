"""
Send functions for Telegram.

License:
    MIT

"""

from loguru import logger
from telegram import Bot, Message, Update
from telegram.error import TelegramError
from telegram.ext import CallbackContext
from telegramify_markdown import markdownify as md


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
        Message | None: The response from the Telegram API, or None if an error occurs.

    """
    lg = logger.bind(chat_id=chat_id, received_id=reply_to_message_id, response_text=text)

    with lg.catch(exception=TelegramError, message="Failed to send message"):
        reply = await bot.send_message(
            chat_id,
            md(text),
            reply_to_message_id=reply_to_message_id,
        )
        lg.bind(response_id=reply.message_id).debug("Reply sent" if reply_to_message_id else "Message sent")
        return reply


async def reply_text(update: Update, context: CallbackContext, text: str) -> None:
    """
    Reply to a message update.

    Convenience method to send a text message in response to an update.

    Args:
        update: the update object
        context: the context object
        text: the text to send

    """
    bot = context.bot
    chat_id = update.effective_message.chat_id
    message_id = update.effective_message.message_id

    await send_text(bot, chat_id, text, message_id)
