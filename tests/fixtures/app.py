"""
General app commands and utility fixtures.

License:
    MIT

"""

import json
from typing import Generator

import pytest
from playwright.async_api import Page

from tests.fixtures.docker_container import KamihiContainer


@pytest.fixture
async def admin_page(kamihi: KamihiContainer, page) -> Page:
    """Fixture that provides the admin page of the Kamihi web interface."""
    await page.goto(f"http://{kamihi.ips.primary}:4242/")
    return page


@pytest.fixture
def user_custom_data():
    """Fixture to provide the user custom data."""
    return {}


@pytest.fixture
def user(kamihi: KamihiContainer, test_settings, user_custom_data) -> Generator[dict, None, None]:
    """Fixture that creates a user in the database."""
    record = kamihi.run_command_and_wait_for_log(
        f"kamihi user add {test_settings.user_id} --data '{json.dumps(user_custom_data)}'",
        level="SUCCESS",
        message="User added",
    )

    yield record["record"]["extra"]


@pytest.fixture
def add_permission_for_user(kamihi: KamihiContainer, test_settings) -> Generator:
    """Fixture that returns a function to add permissions to a user for an action in the database."""

    def _add_permission(user: int, action_name: str):
        kamihi.run_command_and_wait_for_log(
            f"kamihi permission add {action_name} --user {user}",
            level="SUCCESS",
            message="Permission added",
        )

    yield _add_permission


@pytest.fixture
def add_role(kamihi: KamihiContainer, test_settings) -> Generator:
    """Fixture that returns a function to add a role to a user in the database."""

    def _add_role(role_name: str):
        kamihi.run_command_and_wait_for_log(
            f"kamihi role add {role_name}",
            level="SUCCESS",
            message="Role added",
        )

    yield _add_role


@pytest.fixture
def assign_role_to_user(kamihi: KamihiContainer, test_settings) -> Generator:
    """Fixture that returns a function to assign a role to a user in the database."""

    def _assign_role(user: int, role_name: str):
        kamihi.run_command_and_wait_for_log(
            f"kamihi role assign {role_name} {user}",
            level="SUCCESS",
            message="Role assigned",
        )

    yield _assign_role
