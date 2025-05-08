"""
Database connection and table creation.

License:
    MIT

"""

from mongoengine import connect, disconnect


def connect_to_db(url: str) -> None:
    """
    Connect to the database using the provided settings.

    Args:
        url (str): The settings for the bot.

    """
    connect(host=url)


def disconnect_from_db() -> None:
    """Disconnect from the database."""
    disconnect()
