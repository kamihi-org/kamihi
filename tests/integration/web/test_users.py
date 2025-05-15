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
from playwright.async_api import expect


@pytest.mark.asyncio
async def test_kamihi(admin_page, test_user_id):
    await admin_page.get_by_role("link", name=" Users").click()
    await admin_page.get_by_role("link", name="+ New User").click()
    await admin_page.get_by_role("spinbutton", name="Telegram id*").click()
    await admin_page.get_by_role("spinbutton", name="Telegram id*").fill(str(test_user_id))
    await admin_page.get_by_role("button", name="Save", exact=True).click()
    await expect(admin_page.locator("#dt_info")).to_contain_text("Showing 1 to 1 of 1 entries")
    await expect(admin_page.locator("tbody")).to_contain_text(str(test_user_id))
