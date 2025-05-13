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

import pytest

from kamihi.users.models import User
from kamihi.users import *


@pytest.fixture
def user():
    """Fixture to create a test user."""
    user = User(
        telegram_id=123456789,
        is_admin=False,
    ).save()
    yield user
    user.delete()


def test_get_users(user: User):
    """Test the get_users function."""
    res = get_users()

    assert isinstance(res, list)
    assert len(res) == 1
    assert res[0].telegram_id == user.telegram_id
    assert res[0].is_admin == user.is_admin


def test_get_users_empty():
    """Test the get_users function when no users are present."""
    res = get_users()

    assert isinstance(res, list)
    assert len(res) == 0


def test_get_user_from_telegram_id(): ...


def test_get_user_from_telegram_id_not_found(): ...


# @pytest.mark.parametrize
def test_get_user_from_telegram_id_invalid(): ...


def test_is_user_authorized_user(): ...


def test_is_user_authorized_role(): ...


def test_is_user_authorized_admin(): ...


def test_is_user_authorized_action_not_found(): ...
