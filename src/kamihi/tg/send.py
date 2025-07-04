"""
Send functions for Telegram.

License:
    MIT

"""

from __future__ import annotations

import os
import typing
from pathlib import Path

import magic
from loguru import logger
from telegram import Message, Update
from telegram.constants import FileSizeLimit
from telegram.error import TelegramError
from telegram.ext import CallbackContext
from telegramify_markdown import markdownify as md

from .media import *

if typing.TYPE_CHECKING:
    from loguru import Logger


def check_path(file: Path) -> None:
    """
    Check if the file path is valid.

    Args:
        file (Path): The file path to check.

    Raises:
        ValueError: If the file does not exist, is not a file, or no read permission is granted.

    """
    # Validate file exists
    if not file.exists():
        mes = f"File {file} does not exist"
        raise ValueError(mes)

    # Validate it's a file, not a directory
    if not file.is_file():
        mes = f"Path {file} is not a file"
        raise ValueError(mes)

    # Check read permissions
    if not os.access(file, os.R_OK):
        mes = f"File {file} is not readable"
        raise ValueError(mes)


def check_filesize(file: Path, limit: FileSizeLimit) -> None:
    """
    Check if the file size is within the specified limit.

    Args:
        file (Path): The file path to check.
        limit (FileSizeLimit): The maximum allowed file size.

    Raises:
        ValueError: If the file size exceeds the limit.

    """
    if file.stat().st_size > limit:
        mes = f"File {file} exceeds the size limit of {limit} bytes"
        raise ValueError(mes)


def mime(file: Path, lg: Logger) -> str | None:
    """
    Get the MIME type of a file.

    Args:
        file (Path): The file path to check.
        lg (Logger): The logger instance for logging.

    Returns:
        str | None: The MIME type of the file, or None if it cannot be determined.

    """
    check_path(file)

    with lg.catch(exception=magic.MagicException, message="Failed to get MIME type", reraise=True):
        return magic.from_file(file, mime=True)


async def send(obj: Any, update: Update, context: CallbackContext) -> Message | list[Message]:  # noqa: ANN401, C901
    """
    Send a message based on the provided object and annotation.

    Args:
        obj (Any): The object to send.
        update (Update): The Telegram update object containing the chat information.
        context (CallbackContext): The callback context containing the bot instance.

    Returns:
        Message | list[Message]: The response from the Telegram API, or a list of responses if multiple objects are sent.

    Raises:
        TypeError: If the object type is not supported for sending.

    """
    lg = logger.bind(chat_id=update.effective_chat.id, response_text=str(obj))

    if isinstance(obj, str):
        method = context.bot.send_message
        kwargs = {"text": md(obj)}
    elif isinstance(obj, Path):
        lg = lg.bind(path=obj)

        check_path(obj)

        match mime(obj, lg):
            case "image/":
                method = context.bot.send_photo
                limit = FileSizeLimit.PHOTOSIZE_UPLOAD
                kwargs = {"photo": obj, "filename": obj.name}
            case "video/mp4":
                method = context.bot.send_video
                limit = FileSizeLimit.FILESIZE_UPLOAD
                kwargs = {"video": obj, "filename": obj.name}
            case "audio/mpeg" | "audio/mp4" | "audio/x-m4a":
                method = context.bot.send_audio
                limit = FileSizeLimit.FILESIZE_UPLOAD
                kwargs = {"audio": obj, "filename": obj.name}
            case _:
                method = context.bot.send_document
                limit = FileSizeLimit.FILESIZE_UPLOAD
                kwargs = {"document": obj, "filename": obj.name}

        check_filesize(obj, limit)
    elif isinstance(obj, Media):
        caption = md(obj.caption) if obj.caption else None
        lg = lg.bind(path=obj.path, caption=caption)

        if isinstance(obj, Document):
            method = context.bot.send_document
            kwargs = {"document": obj.path, "filename": obj.path.name, "caption": caption}
            limit = FileSizeLimit.FILESIZE_UPLOAD
        elif isinstance(obj, Photo):
            method = context.bot.send_photo
            kwargs = {"photo": obj.path, "filename": obj.path.name, "caption": caption}
            limit = FileSizeLimit.PHOTOSIZE_UPLOAD
        elif isinstance(obj, Video):
            method = context.bot.send_video
            kwargs = {"video": obj.path, "filename": obj.path.name, "caption": caption}
            limit = FileSizeLimit.FILESIZE_UPLOAD
        elif isinstance(obj, Audio):
            method = context.bot.send_audio
            kwargs = {"audio": obj.path, "filename": obj.path.name, "caption": caption}
            limit = FileSizeLimit.FILESIZE_UPLOAD
        else:
            mes = f"Unsupported media type {type(obj)}"
            raise TypeError(mes)

        check_filesize(obj.path, limit)
    elif isinstance(obj, Location):
        method = context.bot.send_location
        kwargs = {"latitude": obj.latitude, "longitude": obj.longitude}
        lg = lg.bind(latitude=obj.latitude, longitude=obj.longitude)
    elif isinstance(obj, (list, tuple)):
        return [await send(item, update, context) for item in obj]
    else:
        mes = f"Object of type {type(obj)} cannot be sent"
        raise TypeError(mes)

    with lg.catch(exception=TelegramError, message="Failed to send"):
        message = await method(
            chat_id=update.effective_chat.id,
            **kwargs,
        )
        lg.bind(response_id=message.message_id).debug("Sent")
        return message
