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


async def send_text(text: str, update: Update, context: CallbackContext) -> Message | None:
    """
    Send a text message to a chat.

    Args:
        text (str): The text message to send.
        update (Update): The Telegram update object containing the chat information.
        context (CallbackContext): The callback context containing the bot instance.

    Returns:
        Message | None: The response from the Telegram API, or None if an error occurs.

    """
    lg = logger.bind(chat_id=update.effective_chat.id, response_text=text)

    with lg.catch(exception=TelegramError, message="Failed to send message"):
        message_reply = await context.bot.send_message(
            update.effective_chat.id,
            md(text if text else ""),
        )
        lg.bind(response_id=message_reply.message_id).debug("Message sent")
        return message_reply


async def send_document(file: Path, update: Update, context: CallbackContext, caption: str = None) -> Message | None:
    """
    Send a file to a chat.

    This function sends a file to a specified chat using the provided bot instance.
    Performs validation checks to ensure the file exists, is readable, and is within size limits.

    Args:
        file (Path): The file to send.
        update (Update): The Telegram update object containing the chat information.
        context (CallbackContext): The callback context containing the bot instance.
        caption (str, optional): The caption for the file. Defaults to None.

    Returns:
        Message | None: The response from the Telegram API, or None if an error occurs.

    """
    lg = logger.bind(chat_id=update.effective_chat.id, path=file)

    if not _check_path(file, lg):
        return None

    with lg.catch(exception=TelegramError, message="Failed to send file"):
        message_reply = await context.bot.send_document(
            chat_id=update.effective_chat.id,
            document=file,
            filename=file.name,
            caption=md(caption) if caption else None,
        )
        lg.bind(response_id=message_reply.message_id).debug("File sent")
        return message_reply


async def send_photo(file: Path, update: Update, context: CallbackContext, caption: str = None) -> Message | None:
    """
    Send a photo to a chat.

    This function sends a photo file to a specified chat using the provided bot instance.
    Performs validation checks to ensure the file exists, is readable, and is within size limits.

    Args:
        file (Path): The photo file to send.
        update (Update): The Telegram update object containing the chat information.
        context (CallbackContext): The callback context containing the bot instance.
        caption (str, optional): The caption for the photo. Defaults to None.

    Returns:
        Message | None: The response from the Telegram API, or None if an error occurs.

    """
    lg = logger.bind(chat_id=update.effective_chat.id, path=file)

    if not _check_path(file, lg, max_size=FileSizeLimit.PHOTOSIZE_UPLOAD):
        return None

    with lg.catch(exception=TelegramError, message="Failed to send file"):
        message_reply = await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=file,
            filename=file.name,
            caption=md(caption) if caption else None,
        )
        lg.bind(response_id=message_reply.message_id).debug("File sent")
        return message_reply
