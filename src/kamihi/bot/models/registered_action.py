"""
RegisteredAction model.

License:
    MIT

"""

from mongoengine import Document, StringField


class RegisteredAction(Document):
    """
    RegisteredAction model.

    This model represents an action that is registered in the system.
    It is used to manage user actions and their associated data.

    Attributes:
        name (str): The name of the action.
        description (str): A description of the action.

    """

    name: str = StringField(required=True, unique=True)
    description: str = StringField()
