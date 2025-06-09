"""
Send functions for Telegram.

License:
    MIT

"""

from __future__ import annotations

import typing
from pathlib import Path

from loguru import logger
from telegram import Bot, Message, Update
from telegram.constants import FileSizeLimit
from telegram.error import TelegramError
from telegram.ext import CallbackContext
from telegramify_markdown import markdownify as md

if typing.TYPE_CHECKING:
    from loguru import Logger


def _send_details(
    context: CallbackContext, update: Update | None = None, chat_id: int = None
) -> tuple[Bot, int | None, int | None, Logger]:
    """
    Get bot, chat ID and message ID for sending a message.

    Args:
        update (Update | None): The Telegram update object, if available.
        context (CallbackContext | None): The callback context, if available.
        chat_id (int | None): The chat ID to send the message to, if provided.

    Returns:
        tuple[Bot, int | None, int | None]: A tuple containing the bot instance, chat ID, and reply_to_message_id.

    """
    bot = context.bot
    reply_id = update.effective_message.message_id if update and update.effective_message else None

    if not chat_id and not bool(update and update.effective_chat and update.effective_chat.id):
        raise ValueError("Cannot determine chat_id. Provide it explicitly or ensure update contains it")

    cid = chat_id or update.effective_chat.id
    lg = logger.bind(chat_id=cid)

    if reply_id:
        lg = lg.bind(reply_to_message_id=reply_id)

    return bot, cid, reply_id, lg


def _check_path(file: Path, lg: Logger, max_size: FileSizeLimit = FileSizeLimit.FILESIZE_UPLOAD) -> bool:
    """
    Check if the file path is valid.

    Args:
        file (Path): The file path to check.
        lg (Logger): The logger instance for logging.
        max_size (FileSizeLimit): The maximum file size allowed. Defaults to FileSizeLimit.FILESIZE_UPLOAD.

    Returns:
        bool: True if the file path is valid, False otherwise.

    """
    # Validate file exists
    if not file.exists():
        lg.error("File does not exist")
        return False

    # Validate it's a file, not a directory
    if not file.is_file():
        lg.error("Path is not a file")
        return False

    # Check read permissions
    try:
        file.read_bytes()
    except PermissionError:
        lg.error("No read permission for file")
        return False

    # Check file size
    file_size = file.stat().st_size
    if file_size > max_size:
        lg.error("File size ({} bytes) exceeds Telegram limit of {} bytes", file_size, max_size)
        return False
    if file_size == 0:
        lg.debug("File is empty, but sending anyway")

    return True


async def send_text(text: str, **kwargs: CallbackContext | Update | int | None) -> Message | None:
    """
    Send a text message to a chat.

    Args:
        text (str): The text message to send.
        kwargs (CallbackContext | Update | int | None): Additional parameters including:
            - context (CallbackContext): The callback context containing the bot instance.
            - update (Update | None): The Telegram update object, if available.
            - chat_id (int | None): The chat ID to send the message to, if provided.

    Returns:
        Message | None: The response from the Telegram API, or None if an error occurs.

    """
    bot, chat_id, reply_to_message_id, lg = _send_details(**kwargs)
    lg = logger.bind(response_text=text)

    with lg.catch(exception=TelegramError, message="Failed to send message"):
        message_reply = await bot.send_message(
            chat_id,
            md(text if text else ""),
            reply_to_message_id=reply_to_message_id,
        )
        lg.bind(response_id=message_reply.message_id).debug("Reply sent" if reply_to_message_id else "Message sent")
        return message_reply


async def send_document(
    file: Path, caption: str = None, **kwargs: CallbackContext | Update | int | None
) -> Message | None:
    """
    Send a file to a chat.

    This function sends a file to a specified chat using the provided bot instance.
    Performs validation checks to ensure the file exists, is readable, and is within size limits.

    Args:
        file (Path): The file to send.
        caption (str, optional): The caption for the file. Defaults to None.
        kwargs (dict): Additional parameters including:
            - context (CallbackContext): The callback context containing the bot instance.
            - update (Update | None): The Telegram update object, if available.
            - chat_id (int | None): The chat ID to send the message to, if provided.

    Returns:
        Message | None: The response from the Telegram API, or None if an error occurs.

    """
    bot, chat_id, reply_to_message_id, lg = _send_details(**kwargs)
    lg = logger.bind(path=file)

    if not _check_path(file, lg):
        return None

    with lg.catch(exception=TelegramError, message="Failed to send file"):
        message_reply = await bot.send_document(
            chat_id=chat_id,
            document=file,
            filename=file.name,
            caption=md(caption) if caption else None,
            reply_to_message_id=reply_to_message_id,
        )
        lg.bind(response_id=message_reply.message_id).debug("File sent")
        return message_reply


async def send_photo(
    file: Path, caption: str = None, **kwargs: CallbackContext | Update | int | None
) -> Message | None:
    """
    Send a photo to a chat.

    This function sends a photo file to a specified chat using the provided bot instance.
    Performs validation checks to ensure the file exists, is readable, and is within size limits.

    Args:
        file (Path): The photo file to send.
        caption (str, optional): The caption for the photo. Defaults to None.
        kwargs (dict): Additional parameters including:
            - context (CallbackContext): The callback context containing the bot instance.
            - update (Update | None): The Telegram update object, if available.
            - chat_id (int | None): The chat ID to send the message to, if provided.

    Returns:
        Message | None: The response from the Telegram API, or None if an error occurs.

    """
    bot, chat_id, reply_to_message_id, lg = _send_details(**kwargs)
    lg = logger.bind(path=file)

    if not _check_path(file, lg, max_size=FileSizeLimit.PHOTOSIZE_UPLOAD):
        return None

    with lg.catch(exception=TelegramError, message="Failed to send photo"):
        message_reply = await bot.send_photo(
            chat_id=chat_id,
            photo=file,
            caption=md(caption) if caption else None,
            filename=file.name,
            reply_to_message_id=reply_to_message_id,
        )
        lg.bind(response_id=message_reply.message_id).debug("Photo sent")
        return message_reply
