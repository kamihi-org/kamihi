"""
Database connection and table creation.

License:
    MIT

"""

from sqlalchemy import Engine
from sqlmodel import SQLModel, create_engine


def get_engine(db_url: str) -> Engine:
    """
    Create a SQLAlchemy engine.

    Args:
        db_url (str): The database URL.

    Returns:
        create_engine: The SQLAlchemy engine.

    """
    return create_engine(db_url)


def create_tables(engine: Engine) -> None:
    """
    Create a table in the database.

    Args:
        engine (Engine): The SQLAlchemy engine.

    """
    SQLModel.metadata.create_all(bind=engine)
