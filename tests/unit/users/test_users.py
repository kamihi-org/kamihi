"""
Unit tests for the users module functions.

License:
    MIT

"""

import pytest

from kamihi.bot.models import RegisteredAction
from kamihi.users.models import User, Role, Permission
from kamihi.users import get_users, get_user_from_telegram_id, is_user_authorized


@pytest.fixture
def user():
    """Fixture to create a test user."""
    user = User(
        telegram_id=123456789,
        is_admin=False,
    ).save()
    yield user
    user.delete()


@pytest.fixture
def role():
    """Fixture to create a test role."""
    role = Role(
        name="test_role",
        users=[],
    ).save()
    yield role
    role.delete()


@pytest.fixture
def reg_action():
    """Fixture to create a test registered action."""
    action = RegisteredAction(
        name="testaction",
        description="Test action",
    ).save()
    yield action
    action.delete()


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


def test_get_user_from_telegram_id(user: User):
    """Test the get_user_from_telegram_id function."""
    res = get_user_from_telegram_id(user.telegram_id)

    assert isinstance(res, User)
    assert res.telegram_id == user.telegram_id
    assert res.is_admin == user.is_admin


def test_get_user_from_telegram_id_not_found():
    """Test the get_user_from_telegram_id function when user is not found."""
    res = get_user_from_telegram_id(999999999)

    assert res is None


@pytest.mark.parametrize(
    "telegram_id",
    [
        "333333333",
        444444444.0,
        None,
        -1,
    ],
)
def test_get_user_from_telegram_id_invalid(telegram_id):
    """Test the get_user_from_telegram_id function with invalid telegram_id."""
    res = get_user_from_telegram_id(telegram_id)

    assert res is None


def test_is_user_authorized_user(user, reg_action):
    """Test the is_user_authorized function for a regular user."""
    permission = Permission(
        action=reg_action,
        users=[user],
        roles=[],
    ).save()

    res = is_user_authorized(user, reg_action.name)

    assert res is True

    permission.delete()


def test_is_user_authorized_role(user, role, reg_action):
    """Test the is_user_authorized function for a user with a role."""
    permission = Permission(
        action=reg_action,
        users=[],
        roles=[role],
    ).save()

    role.users.append(user)
    role.save()

    res = is_user_authorized(user, reg_action.name)

    assert res is True

    permission.delete()


def test_is_user_authorized_admin(user, reg_action):
    """Test the is_user_authorized function for an admin user."""
    user.is_admin = True
    user.save()

    res = is_user_authorized(user, reg_action.name)

    assert res is True


def test_is_user_authorized_action_not_found(user):
    """Test the is_user_authorized function when action is not found."""
    res = is_user_authorized(user, "non_existent_action")

    assert res is False
