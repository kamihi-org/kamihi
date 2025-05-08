"""
Action model.

License:
    MIT

"""

from mongoengine import *


class Action(Document):
    """
    Action model for Kamihi bot.

    This model represents an action that can be performed by the bot. It includes
    the name, commands, description, and function associated with the action.

    Attributes:
        name (str): The name of the action.
        commands (list[str]): List of commands associated with the action.
        description (str): Description of the action.

    """

    name: str = StringField(unique=True, required=True)
    commands: list[str] = ListField(StringField(), required=True)
    description: str = StringField()
