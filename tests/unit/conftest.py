"""
Unit testing configuration and common fixtures.

License:
    MIT

"""

import random
from unittest import mock
from unittest.mock import Mock, AsyncMock

import mongomock
import pytest
from mongoengine import connect
from telegram import Update, Bot, Message
from telegram.constants import LocationLimit

from kamihi.db.mongo import disconnect
from kamihi.tg.media import Location
from tests.conftest import random_image, random_video_path, random_audio_path, random_voice_note_path


@pytest.fixture
def mock_update():
    """Fixture to provide a mock Update instance."""
    update = Mock(spec=Update)
    update.effective_message = Mock()
    update.effective_message.chat_id = 123456
    update.effective_message.message_id = 789
    return update


@pytest.fixture
def mock_context():
    """Fixture to provide a mock CallbackContext."""
    context = Mock()
    context.bot = Mock(spec=Bot)
    context.bot.send_message = AsyncMock(return_value=Mock(spec=Message))
    return context


@pytest.fixture(scope="session", autouse=True)
def mock_mongodb():
    """Fixture to provide a mock MongoDB instance."""
    connect("kamihi_test", host="mongodb://localhost", alias="default", mongo_client_class=mongomock.MongoClient)
    with mock.patch("kamihi.bot.bot.connect"), mock.patch("kamihi.db.mongo.connect"):
        yield
    disconnect()


@pytest.fixture
def tmp_file(tmp_path):
    """Fixture to provide a mock file path."""
    file = tmp_path / "test_file.txt"
    file.write_text("This is a test file.")
    return file


@pytest.fixture
def tmp_image_file(tmp_path):
    """Fixture to create a random image in a temporal directory and provide its path."""
    file = tmp_path / "test_file.jpg"

    with open(file, "wb") as f:
        f.write(random_image())

    return file


@pytest.fixture
def tmp_video_file(tmp_path):
    """Fixture that provides a random video file path."""
    return random_video_path()


@pytest.fixture
def tmp_audio_file():
    """Fixture that provides a random audio file path."""
    return random_audio_path()


@pytest.fixture
def tmp_voice_file():
    """Fixture that provides a random voice note file path."""
    return random_voice_note_path()


@pytest.fixture
def random_location():
    """Fixture to provide a random Location object."""
    latitude = random.uniform(-90.0, 90.0)
    longitude = random.uniform(-180.0, 180.0)
    horizontal_accuracy = random.uniform(0.0, float(LocationLimit.HORIZONTAL_ACCURACY))
    return Location(latitude=latitude, longitude=longitude, horizontal_accuracy=horizontal_accuracy)
