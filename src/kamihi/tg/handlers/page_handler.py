"""
Pages handler.

License:
    MIT
"""

from loguru import logger
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from telegramify_markdown import markdownify as md

from kamihi.tg.media import Pages


async def page_callback(update: Update, context: CallbackContext) -> int:
    """
    Handle page callbacks.

    Args:
        update (Update): Update object
        context (CallbackContext): CallbackContext object

    """
    query = update.callback_query
    pages_id = query.data.split("#")[0]
    page_num = int(query.data.split("#")[1]) - 1

    await context.bot.answer_callback_query(query.id)

    lg = logger.bind(message_id=query.message.message_id, pages_id=pages_id, page_num=page_num)
    lg.trace("Handling page callback")

    try:
        page, keyboard = Pages.from_id(pages_id).get_page(page_num)
    except ValueError:
        lg.debug("Query refers to non-existing pages, possibly because they expired")
        page = md("⚠️ *This paginated message has expired.*")
        keyboard = None

    await query.edit_message_text(text=page, reply_markup=keyboard, parse_mode="MarkdownV2")

    lg.bind(text=page).debug("Handled page callback")

    return ConversationHandler.END
