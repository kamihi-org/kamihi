"""
Send functions for Telegram.

License:
    MIT

"""

from __future__ import annotations

import collections.abc
import typing
from io import BufferedReader
from pathlib import Path
from typing import Any

import magic
from loguru import logger
from telegram import Message, Update
from telegram.error import TelegramError
from telegram.ext import CallbackContext
from telegramify_markdown import markdownify as md

from .media import Audio, Document, Location, Media, Photo, Video, Voice

if typing.TYPE_CHECKING:
    from loguru import Logger  # skipcq: TCV-001


def guess_media_type(file: Path | bytes | BufferedReader, lg: Logger) -> Media:
    """
    Guess the media type of a file based on its MIME type.

    Args:
        file (Path | bytes | BufferedReader): The file path to check.
        lg (Logger): The logger instance to use for logging.

    Returns:
        Media: An instance of Media subclass based on the file type.

    """
    with lg.catch(exception=magic.MagicException, message="Failed to get MIME type", reraise=True):
        if isinstance(file, bytes):
            mimetype = magic.from_buffer(file, mime=True)
        elif isinstance(file, BufferedReader):
            file.seek(0)
            mimetype = magic.from_buffer(file.read(1024), mime=True)
            file.seek(0)
        else:
            mimetype = magic.from_file(file, mime=True)
        lg.trace("MIME type is {t}", t=mimetype)

    if "image/" in mimetype:
        lg.debug("File detected as image")
        return Photo(file=file, filename=file.name if isinstance(file, Path) else None)

    if mimetype == "video/mp4":
        lg.debug("File detected as video")
        return Video(file=file, filename=file.name if isinstance(file, Path) else None)

    if mimetype in ("audio/mpeg", "audio/mp4", "audio/x-m4a", "audio/ogg"):
        try:
            res = Voice(file=file, filename=file.name if isinstance(file, Path) else None)
            lg.debug("File detected as voice message")
        except ValueError:
            res = Audio(file=file, filename=file.name if isinstance(file, Path) else None)
            lg.debug("File detected as audio")
        return res

    lg.debug("File detected as generic document")
    return Document(file=file, filename=file.name if isinstance(file, Path) else None)


# skipcq: PY-R1000
async def send(obj: Any, update: Update, context: CallbackContext) -> Message | list[Message]:  # noqa: ANN401, C901
    """
    Send a message based on the provided object and annotation.

    Args:
        obj (Any): The object to send.
        update (Update): The Telegram update object containing the chat information.
        context (CallbackContext): The callback context containing the bot instance.

    Returns:
        Message | list[Message]: The response from the Telegram API, or a list of responses
            if multiple objects are sent.

    Raises:
        TypeError: If the object type is not supported for sending.

    """
    lg = logger.bind(chat_id=update.effective_chat.id)

    if isinstance(obj, str):
        lg = lg.bind(text=obj)
        method = context.bot.send_message
        kwargs = {"text": md(obj)}
        lg.debug("Sending as text message")
    elif isinstance(obj, (Path, bytes, BufferedReader)):
        return await send(guess_media_type(obj, lg), update, context)
    elif isinstance(obj, Media):
        caption = md(obj.caption) if obj.caption else None
        lg = lg.bind(path=obj.file, caption=caption)

        kwargs: dict[str, Any] = {"filename": obj.filename, "caption": caption}

        if isinstance(obj, Document):
            method = context.bot.send_document
            kwargs["document"] = obj.file
            lg.debug("Sending as generic file")
        elif isinstance(obj, Photo):
            method = context.bot.send_photo
            kwargs["photo"] = obj.file
            lg.debug("Sending as photo")
        elif isinstance(obj, Video):
            method = context.bot.send_video
            kwargs["video"] = obj.file
            lg.debug("Sending as video")
        elif isinstance(obj, Audio):
            method = context.bot.send_audio
            kwargs["audio"] = obj.file
            lg.debug("Sending as audio")
        elif isinstance(obj, Voice):
            method = context.bot.send_voice
            kwargs["voice"] = obj.file
            lg.debug("Sending as voice note")
        else:
            mes = f"Object of type {type(obj)} cannot be sent"
            raise TypeError(mes)
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
    elif (
        isinstance(obj, collections.abc.Sequence)
        and 2 <= len(obj) <= 10
        and all(isinstance(item, Path) for item in obj)
    ):
        lg.debug("Received list of file paths, guessing media types and trying to send as media group")
        return await send(
            [guess_media_type(item, lg) for item in obj],
            update,
            context,
        )
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
