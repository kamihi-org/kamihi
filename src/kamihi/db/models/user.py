"""
User model.

License:
    MIT

"""

from mongoengine import *


class User(Document):
    """Placeholder for the User model."""

    _model = None

    telegram_id: str = StringField(required=True, unique=True)

    meta = {"allow_inheritance": True}

    @classmethod
    def get_model(cls) -> type["User"]:
        """
        Get the model class for the User.

        Returns:
            type: The model class for the User.

        """
        return cls if cls._model is None else cls._model

    @classmethod
    def set_model(cls, model: type["User"]) -> None:
        """
        Set the model class for the User.

        Args:
            model (type): The model class to set.

        """
        cls._model = model
