"""
Send functions for Telegram.

License:
    MIT

"""

from pathlib import Path

from loguru import logger
from telegram import Bot, Message, Update
from telegram.constants import FileSizeLimit
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


async def send_file(bot: Bot, chat_id: int, file: Path, reply_to_message_id: int = None) -> Message | None:
    """
    Send a file to a chat.

    This function sends a file to a specified chat using the provided bot instance.
    Performs validation checks to ensure the file exists, is readable, and is within size limits.

    Args:
        bot (Bot): The Telegram Bot instance.
        chat_id (int): The ID of the chat to send the file to.
        file (Path): The file to send.
        reply_to_message_id (int, optional): The ID of the message to reply to. Defaults to None.

    Returns:
        Message | None: The response from the Telegram API, or None if an error occurs.

    """
    lg = logger.bind(chat_id=chat_id, received_id=reply_to_message_id, path=file)

    # Validate file exists
    if not file.exists():
        lg.error("File does not exist")
        return None

    # Validate it's a file, not a directory
    if not file.is_file():
        lg.error("Path is not a file")
        return None

    # Check read permissions
    try:
        file.read_text()
    except PermissionError:
        lg.error("No read permission for file")
        return None

    # Check file size
    file_size = file.stat().st_size
    max_size = FileSizeLimit.FILESIZE_UPLOAD
    if file_size > max_size:
        lg.error("File size ({} bytes) exceeds Telegram limit of {} bytes", file_size, max_size)
        return None
    if file_size == 0:
        lg.warning("File is empty")

    with lg.catch(exception=TelegramError, message="Failed to send file"):
        reply = await bot.send_document(
            chat_id=chat_id,
            document=file,
            filename=file.name,
            reply_to_message_id=reply_to_message_id,
        )
        lg.bind(response_id=reply.message_id).debug("File sent")
        return reply


async def send(bot: Bot, chat_id: int, content: str | Path, reply_to_message_id: int = None) -> Message | None:
    """
    Send a message to a chat.

    This function sends a message to a specified chat using the provided bot instance.
    It can handle text and files.

    Args:
        bot (Bot): The Telegram Bot instance.
        chat_id (int): The ID of the chat to send the message to.
        content (str | Path): The content to send, which can be text or a file.
        reply_to_message_id (int, optional): The ID of the message to reply to. Defaults to None.

    Returns:
        Message | None: The response from the Telegram API, or None if an error occurs.

    """
    match content:
        case str():
            return await send_text(bot, chat_id, content, reply_to_message_id)
        case Path():
            return await send_file(bot, chat_id, content, reply_to_message_id)
        case _:
            logger.error("Unsupported content type: {}", type(content))
            return None


async def reply(
    update: Update,
    context: CallbackContext,
    content: str | Path,
) -> Message | None:
    """
    Reply to a message update.

    This function replies to a message update with either text or a file.

    Args:
        update: the update object
        context: the context object
        content: the content to send, which can be text or a file

    Returns:
        Message | None: The response from the Telegram API, or None if an error occurs.

    """
    bot = context.bot
    chat_id = update.effective_message.chat_id
    message_id = update.effective_message.message_id

    return await send(bot, chat_id, content, reply_to_message_id=message_id)
