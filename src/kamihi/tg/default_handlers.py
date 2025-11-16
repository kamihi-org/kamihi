"""
Default handlers.

License:
    MIT

"""

from loguru import logger
from telegram import Update
from telegram.ext import ApplicationHandlerStop, CallbackContext

from kamihi.base import get_settings

from .send import send


async def default(update: Update, context: CallbackContext) -> None:
    """
    Tells the user their message is not understood.

    Args:
        update (Update): Update object
        context (CallbackContext): CallbackContext object

    """
    settings = get_settings().responses

    logger.bind(chat_id=update.effective_message.chat_id, message_id=update.effective_message.message_id).debug(
        "Received message but no handler matched, so sending default response"
    )

    await send(settings.default_message, chat_id=update.effective_message.chat_id, context=context)
    raise ApplicationHandlerStop


async def error(update: object | None, context: CallbackContext) -> None:
    """
    Apologizes to the user when an error happens.

    Args:
        update (Update): Update object
        context (CallbackContext): CallbackContext object

    """
    settings = get_settings().responses

    logger.opt(exception=context.error).error("An error occurred")

    if isinstance(update, Update):
        await send(settings.error_message, chat_id=update.effective_message.chat_id, context=context)

    raise ApplicationHandlerStop


async def cancel(update: Update, context: CallbackContext) -> None:
    """
    Cancel the current operation.

    Args:
        update (Update): Update object
        context (CallbackContext): CallbackContext object

    """
    logger.bind(chat_id=update.effective_message.chat_id, message_id=update.effective_message.message_id).info(
        "User requested to cancel the current operation"
    )

    text = context.bot_data["responses"]["cancel_message"]
    await send(text, chat_id=update.effective_message.chat_id, context=context)
    raise ApplicationHandlerStop
