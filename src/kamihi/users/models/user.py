"""
User model.

License:
    MIT

"""

from mongoengine import BooleanField, Document, IntField
from starlette.requests import Request


class User(Document):
    """Placeholder for the User model."""

    telegram_id: int = IntField(required=True, unique=True)
    is_admin: bool = BooleanField(default=False)

    meta = {"allow_inheritance": True}

    _model = None

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

    def __str__(self) -> str:
        """Representation of the User model."""
        return f"{self.telegram_id}"

    async def __admin_repr__(self, request: Request) -> str:
        """Representation of the User model in the admin interface."""
        return str(self)
