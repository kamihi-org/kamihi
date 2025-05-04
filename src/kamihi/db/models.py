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

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

base = declarative_base()


class Base(base):
    """Base model for all database models."""

    __abstract__ = True
    uid = Column(Integer, primary_key=True, autoincrement=True)


class User(Base):
    """Provisional user model."""

    __tablename__ = "user"
    telegram_id: Mapped[str] = mapped_column(String())
