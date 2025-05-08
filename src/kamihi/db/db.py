"""
Database connection and table creation.

License:
    MIT

"""

from mongoengine import connect

from kamihi.base.config import KamihiSettings


def connect_to_db(settings: KamihiSettings) -> None:
    """
    Connect to the database using the provided settings.

    Args:
        settings (KamihiSettings): The settings for the bot.

    """
    connect(host=settings.db_url)
