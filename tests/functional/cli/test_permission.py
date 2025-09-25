"""
Functional tests for the CLI permission command.

License:
    MIT

"""

import pytest
from playwright.async_api import Page, expect
from telethon.tl.custom import Conversation

from tests.functional.conftest import KamihiContainer


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "actions_folder",
    [
        {
            "start/__init__.py": "",
            "start/start.py": """\
                from kamihi import bot
                
                @bot.action
                async def start():
                    return "test"
            """,
        }
    ],
)
async def test_permission_add_user(kamihi: KamihiContainer, user: dict, admin_page: Page, chat: Conversation, actions_folder):
    """Test the permission add command."""
    kamihi.run_command_and_wait_for_log(
        f"kamihi permission add start --user {user['telegram_id']}",
        level="SUCCESS",
        message="Permission added",
    )

    await admin_page.get_by_role("link", name=" Permissions").click()
    await expect(admin_page.locator("[id=\"\\31 \"]")).to_contain_text("/start")
    await expect(admin_page.locator("[id=\"\\31 \"]")).to_contain_text(str(user["telegram_id"]))
    await expect(admin_page.locator("[id=\"\\31 \"]")).to_contain_text("-empty-")

    await chat.send_message("/start")
    response = await chat.get_response()

    assert response.text == "test"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "actions_folder",
    [
        {
            "start/__init__.py": "",
            "start/start.py": """\
                from kamihi import bot
                
                @bot.action
                async def start():
                    return "test"
            """,
        }
    ],
)
async def test_permission_add_role(
    kamihi: KamihiContainer, user: dict, add_role, assign_role_to_user, admin_page, chat: Conversation, actions_folder
):
    """Test the permission add command with a role."""
    add_role("test")
    assign_role_to_user(user["telegram_id"], "test")

    kamihi.run_command_and_wait_for_log(
        "kamihi permission add start --role test",
        level="SUCCESS",
        message="Permission added",
    )

    await admin_page.get_by_role("link", name=" Permissions").click()
    await expect(admin_page.locator("[id=\"\\31 \"]")).to_contain_text("/start")
    await expect(admin_page.locator("[id=\"\\31 \"]")).to_contain_text("-empty-")
    await expect(admin_page.locator("[id=\"\\31 \"]")).to_contain_text("test")

    await chat.send_message("/start")
    response = await chat.get_response()

    assert response.text == "test"


def test_permission_add_no_args(kamihi: KamihiContainer):
    """Test the permission add command without users or roles specified."""
    kamihi.run_command_and_wait_for_message(
        "kamihi permission add",
        "Missing argument 'ACTION'",
    )


def test_permission_add_invalid_action(kamihi: KamihiContainer):
    """Test the permission add command with an invalid action."""
    kamihi.run_command_and_wait_for_log(
        "kamihi permission add invalid_action --user 123456789", "Action not found", "ERROR", {"name": "invalid_action"}
    )
