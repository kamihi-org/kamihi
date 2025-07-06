"""
Send functions for Telegram.

License:
    MIT

"""

from __future__ import annotations

import collections.abc
import os
import typing
from pathlib import Path
from typing import Any

import magic
from loguru import logger
from telegram import Message, Update
from telegram.constants import FileSizeLimit
from telegram.error import TelegramError
from telegram.ext import CallbackContext
from telegramify_markdown import markdownify as md

from .media import Audio, Document, Location, Media, Photo, Video

if typing.TYPE_CHECKING:
    from loguru import Logger


def check_file(file: Path) -> None:
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


def guess_media_type(file: Path, lg: Logger) -> Media:
    """
    Guess the media type of a file based on its MIME type.

    Args:
        file (Path): The file path to check.
        lg (Logger): The logger instance to use for logging.

    Returns:
        Media: An instance of Media subclass based on the file type.

    """
    lg = lg.bind(path=file)

    check_file(file)

    with lg.catch(exception=magic.MagicException, message="Failed to get MIME type", reraise=True):
        mimetype = magic.from_file(file, mime=True)
        lg.trace("MIME type is {t}", t=mimetype)

    if "image/" in mimetype:
        lg.debug("File detected as image")
        return Photo(path=file, filename=file.name)

    if mimetype == "video/mp4":
        lg.debug("File detected as video")
        return Video(path=file, filename=file.name)

    if mimetype in ("audio/mpeg", "audio/mp4", "audio/x-m4a"):
        lg.debug("File detected as audio")
        return Audio(path=file, filename=file.name)

    lg.debug("File detected as generic document")
    return Document(path=file, filename=file.name)


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
    lg = logger.bind(chat_id=update.effective_chat.id)

    if isinstance(obj, str):
        lg = lg.bind(text=obj)
        method = context.bot.send_message
        kwargs = {"text": md(obj)}
        lg.debug("Sending as text message")
    elif isinstance(obj, Path):
        return await send(guess_media_type(obj, lg), update, context)
    elif isinstance(obj, Media):
        caption = md(obj.caption) if obj.caption else None
        lg = lg.bind(path=obj.path, caption=caption)

        kwargs: dict[str, Any] = {"filename": obj.path.name, "caption": caption}
        limit = FileSizeLimit.FILESIZE_UPLOAD

        if isinstance(obj, Document):
            method = context.bot.send_document
            kwargs["document"] = obj.path
            lg.debug("Sending as generic file")
        elif isinstance(obj, Photo):
            method = context.bot.send_photo
            kwargs["photo"] = obj.path
            limit = FileSizeLimit.PHOTOSIZE_UPLOAD
            lg.debug("Sending as photo")
        elif isinstance(obj, Video):
            method = context.bot.send_video
            kwargs["video"] = obj.path
            lg.debug("Sending as video")
        elif isinstance(obj, Audio):
            method = context.bot.send_audio
            kwargs["audio"] = obj.path
            lg.debug("Sending as audio")
        else:
            mes = f"Object of type {type(obj)} cannot be sent"
            raise TypeError(mes)

        check_file(obj.path)
        check_filesize(obj.path, limit)
    elif isinstance(obj, Location):
        lg = lg.bind(latitude=obj.latitude, longitude=obj.longitude, horizontal_accuracy=obj.horizontal_accuracy)
        method = context.bot.send_location
        kwargs = {"latitude": obj.latitude, "longitude": obj.longitude, "horizontal_accuracy": obj.horizontal_accuracy}
        lg.debug("Sending as location")
    elif (
        isinstance(obj, collections.abc.Sequence)
        and 2 <= len(obj) <= 10
        and any(
            [
                all(isinstance(item, (Photo, Video)) for item in obj),
                all(isinstance(item, Document) for item in obj),
                all(isinstance(item, Audio) for item in obj),
            ]
        )
    ):
        lg.debug("Sending as media group")
        method = context.bot.send_media_group
        kwargs = {"media": [item.as_input_media() for item in obj]}
    elif isinstance(obj, collections.abc.Sequence):
        lg.debug("Sending as list of items")
        return [await send(item, update, context) for item in obj]
    else:
        mes = f"Object of type {type(obj)} cannot be sent"
        raise TypeError(mes)

    with lg.catch(exception=TelegramError, message="Failed to send"):
        res = await method(
            chat_id=update.effective_chat.id,
            **kwargs,
        )
        lg.bind(
            response_id=res.message_id if isinstance(res, Message) else [message.message_id for message in res],
        ).debug("Sent")
        return res
