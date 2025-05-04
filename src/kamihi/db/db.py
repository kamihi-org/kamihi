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

from sqlalchemy import Engine, create_engine

from kamihi.db.models import Base


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
    Base.metadata.create_all(bind=engine)
