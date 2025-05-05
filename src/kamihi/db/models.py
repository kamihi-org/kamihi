"""
Database models.

License:
    MIT

"""

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """Placeholder for the User model."""

    id: int | None = Field(default=None, primary_key=True)
    telegram_id: int
