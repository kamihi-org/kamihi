"""
Connection management to MongoDB using MongoEngine.

License:
    MIT

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
        host=settings.host + "/" + settings.name,
        alias="default",
    )


def disconnect() -> None:
    """Disconnect from the MongoDB database."""
    mongo_disconnect(alias="default")
