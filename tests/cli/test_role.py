"""
Functional tests for the CLI permission command.

License:
    MIT

"""

import pytest
from playwright.async_api import Page, expect

from tests.fixtures.docker_container import KamihiContainer


@pytest.mark.asyncio
async def test_role_add(kamihi: KamihiContainer, admin_page: Page):
    """Test the role add command."""
    kamihi.run_command_and_wait_for_log(
        "kamihi role add testrole",
        level="SUCCESS",
        message="Role added",
    )

    await admin_page.get_by_role("link", name=" Roles").click()
    await expect(admin_page.locator('[id="\\31 "]')).to_contain_text("testrole")


def test_role_add_existing(kamihi: KamihiContainer):
    """Test adding an existing role."""
    kamihi.run_command_and_wait_for_log(
        "kamihi role add testrole",
        level="SUCCESS",
        message="Role added",
    )
    kamihi.run_command_and_wait_for_log(
        "kamihi role add testrole",
        level="ERROR",
        message="Role already exists",
    )


@pytest.mark.asyncio
async def test_role_assign(kamihi: KamihiContainer, user: dict, add_role, admin_page: Page):
    """Test the role assign command."""
    add_role("testrole")

    kamihi.run_command_and_wait_for_log(
        f"kamihi role assign testrole {user['telegram_id']}",
        level="SUCCESS",
        message="Role assigned",
    )

    await admin_page.get_by_role("link", name=" Roles").click()
    await expect(admin_page.locator('[id="\\31 "]')).to_contain_text("testrole")
    await expect(admin_page.locator('[id="\\31 "]')).to_contain_text(str(user["telegram_id"]))


def test_role_assign_repeated(kamihi: KamihiContainer, user: dict, add_role):
    """Test assigning a user to a role they already have."""
    add_role("testrole")

    kamihi.run_command_and_wait_for_log(
        f"kamihi role assign testrole {user['telegram_id']}",
        level="SUCCESS",
        message="Role assigned",
    )

    kamihi.run_command_and_wait_for_log(
        f"kamihi role assign testrole {user['telegram_id']}",
        level="WARNING",
        message="User already has role, skipping...",
    )


def test_role_assign_nonexistent_role(kamihi: KamihiContainer, user: dict):
    """Test assigning a user to a non-existent role."""
    kamihi.run_command_and_wait_for_log(
        f"kamihi role assign nonexistrole {user['telegram_id']}",
        level="ERROR",
        message="Role does not exist",
    )


def test_role_assign_nonexistent_user(kamihi: KamihiContainer, add_role):
    """Test assigning a non-existent user to a role."""
    add_role("testrole")

    kamihi.run_command_and_wait_for_log(
        "kamihi role assign testrole 999999999",
        level="WARNING",
        message="User not found, skipping...",
    )
