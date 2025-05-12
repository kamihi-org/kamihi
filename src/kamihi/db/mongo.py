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

from mongoengine import connect as mongo_connect
from mongoengine import disconnect as mongo_disconnect

from kamihi.base.config import DatabaseSettings


def connect(settings: DatabaseSettings) -> None:
    """
    Connect to the MongoDB database.

    This function establishes a connection to the MongoDB database using the
    configuration settings defined in the Kamihi settings module.

    Args:
        settings (DatabaseSettings): The database settings for the connection

    """
    mongo_connect(
        db=settings.name,
        host=settings.host,
        alias="default",
        connect=False,
    )


def disconnect() -> None:
    """Disconnect from the MongoDB database."""
    mongo_disconnect(alias="default")
