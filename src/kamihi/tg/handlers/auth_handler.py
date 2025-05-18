"""
Custom handler for Telegram bot that checks if a user is authorized to use a wrapped handler.

License:
    MIT

"""

from loguru import logger
from telegram import Update
from telegram.ext import BaseHandler

from kamihi.users import get_user_from_telegram_id, is_user_authorized


class AuthHandler(BaseHandler):
    """
    Custom wrapper handler that checks if the user is authorized to use the wrapped handler before executing it.

    Attributes:
        handler (BaseHandler): the handler to be wrapped.
        name (str): The name of the action.

    """

    handler: BaseHandler
    name: str

    def __init__(self, handler: BaseHandler, name: str) -> None:
        """Initialize the AuthHandler with the callback function."""
        self.handler = handler
        self.name = name
        super().__init__(self.handler.callback)

    def check_update(self, update: Update) -> bool:
        """Determine if an update should be handled by this handler instance."""
        if not isinstance(update, Update):
            return False

        if update.message and update.effective_user:
            user = get_user_from_telegram_id(update.effective_user.id)

            if user is None:
                logger.bind(user_id=update.effective_user.id, action=self.name).debug(
                    "User not found in the database tried to use action."
                )
                return False

            if not is_user_authorized(user, self.name):
                logger.bind(user_id=user.telegram_id, action=self.name).debug(
                    "User is not authorized to use this action."
                )
                return False

        return self.handler.check_update(update)
