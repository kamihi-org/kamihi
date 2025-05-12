"""
TODO: one-line module description.

TODO: Additional details about the module, its purpose, and any necessary
background information. Explain what functions or classes are included.

License:
    MIT

Examples:
    [Examples of how to use the module/classes/functions]

Attributes:
    [List any relevant module-level attributes with types and descriptions]

"""

from loguru import logger
from telegram import Update
from telegram.ext import BaseHandler

from kamihi.users.users import get_user_from_telegram_id, is_user_authorized


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

            if user and is_user_authorized(user, self.name):
                return True

        return False
