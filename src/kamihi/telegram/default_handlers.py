"""
Default handlers.

License:
    MIT

"""

from loguru import logger
from telegram import Update
from telegram.ext import CallbackContext

from kamihi.telegram.send import reply_text


async def default(update: Update, context: CallbackContext) -> None:
    """
    Tells the user their message is not understood.

    Args:
        update (Update): Update object
        context (CallbackContext): CallbackContext object

    """
    logger.bind(chat_id=update.effective_message.chat_id, message_id=update.effective_message.message_id).debug(
        "Message has no handler, so sending default response"
    )

    text = context.bot_data.get("responses").get("default_text")
    await reply_text(update, context, text)


async def error(update: object | None, context: CallbackContext) -> None:
    """
    Apologizes to the user when an error happens.

    Args:
        update (Update): Update object
        context (CallbackContext): CallbackContext object

    """
    logger.opt(exception=context.error).error("An error occurred")

    if isinstance(update, Update):
        text = context.bot_data.get("responses").get("error_text")
        await reply_text(update, context, text)
