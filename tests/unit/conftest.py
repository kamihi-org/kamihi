"""
Unit testing configuration and common fixtures.

License:
    MIT

"""

from unittest import mock
from unittest.mock import Mock, AsyncMock

import mongomock
import pytest
from mongoengine import connect
from telegram import Update, Bot, Message

from kamihi.db.mongo import disconnect


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
