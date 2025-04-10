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
from telegram import Update
from telegram.ext import CallbackContext

from kamihi.telegram.send import send_text


async def default(update: Update, context: CallbackContext) -> None:
    """
    Tells the user their message is not understood.

    Args:
        update (Update): Update object
        context (CallbackContext): CallbackContext object

    """
    bot = context.bot
    chat_id = update.effective_message.chat_id
    message_id = update.effective_message.message_id
    text = context.bot_data.get("responses").get("default").get("text")

    logger.bind(chat_id=chat_id, message_id=message_id).debug("Message has no handler, so sending default response")

    await send_text(bot, chat_id, text, message_id)


async def unknown_command(update: Update, context: CallbackContext) -> None:
    """
    Tells the user their command is not understood.

    Args:
        update (Update): Update object
        context (CallbackContext): CallbackContext object

    """
    bot = context.bot
    chat_id = update.effective_message.chat_id
    message_id = update.effective_message.message_id
    text = context.bot_data.get("responses").get("unknown_command").get("text")

    logger.bind(chat_id=chat_id, message_id=message_id).debug("Unknown command received")

    await send_text(bot, chat_id, text, message_id)


async def error(update: Update, context: CallbackContext) -> None:
    """
    Apologizes to the user when an error happens.

    Args:
        update (Update): Update object
        context (CallbackContext): CallbackContext object

    """
    bot = context.bot
    chat_id = update.effective_message.chat_id
    message_id = update.effective_message.message_id
    text = context.bot_data.get("responses").get("error").get("text")

    logger.bind(chat_id=chat_id, message_id=message_id).debug("Notifying user of error")

    await send_text(bot, chat_id, text, message_id)
