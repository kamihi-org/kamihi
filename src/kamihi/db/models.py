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

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """Placeholder for the User model."""

    id: int | None = Field(default=None, primary_key=True)
    telegram_id: int
