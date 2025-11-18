"""
Test cases for bot actions that return locations.

License:
    MIT

"""
import random

import pytest
from telethon.tl.custom import Conversation, Message

from kamihi.tg.media import Location


def random_location() -> Location:
    """
    Generates a random location with latitude and longitude.

    Returns:
        tuple[float, float]: A tuple containing latitude and longitude.

    """
    latitude = random.uniform(-90.0, 90.0)
    longitude = random.uniform(-180.0, 180.0)
    return Location(latitude=latitude, longitude=longitude)


@pytest.mark.asyncio
@pytest.mark.usefixtures("kamihi")
@pytest.mark.parametrize(
    "actions_folder",
    [
        {
            "start/__init__.py": "",
            "start/start.py": f"""\
                from kamihi import bot
                             
                @bot.action
                async def start():
                    return bot.Location(latitude={random_location().latitude}, longitude={random_location().latitude})
            """,
        },
    ],
)
async def test_location(user, add_permission_for_user, chat: Conversation, actions_folder):
    """Test that the action sends a location to Telegram when a Location is returned."""
    add_permission_for_user(user["telegram_id"], "start")

    await chat.send_message("/start")
    response: Message = await chat.get_response()

    assert response.geo is not None
