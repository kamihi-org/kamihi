"""
Functional tests for user management through the web interface.

License:
    MIT

"""

import pytest
from playwright.async_api import Page, expect


@pytest.mark.asyncio
async def test_create_user(admin_page: Page, test_settings):
    """Test the creation of a user through the web interface."""
    await admin_page.get_by_role("link", name=" Users").click()
    await admin_page.get_by_role("link", name="+ New User").click()
    await admin_page.get_by_role("spinbutton", name="Telegram id*").click()
    await admin_page.get_by_role("spinbutton", name="Telegram id*").fill(str(test_settings.user_id))
    await admin_page.get_by_role("button", name="Save", exact=True).click()
    await expect(admin_page.locator("#dt_info")).to_contain_text("Showing 1 to 1 of 1 entries")
    await expect(admin_page.locator("tbody")).to_contain_text(str(test_settings.user_id))
