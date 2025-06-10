"""
Functional tests for the CLI user command.

License:
    MIT

"""

import pytest
from playwright.async_api import Page, expect


from tests.functional.conftest import KamihiContainer


@pytest.mark.asyncio
async def test_user_add(kamihi: KamihiContainer, admin_page: Page):
    """Test adding a user with valid parameters."""
    kamihi.run_and_wait_for_log(
        "kamihi user add 123456789",
        "User added.",
        "SUCCESS",
        {"telegram_id": 123456789, "is_admin": False},
    )
    await admin_page.get_by_role("link", name=" Users").click()
    await expect(admin_page.locator("#dt_info")).to_contain_text("Showing 1 to 1 of 1 entries")
    await expect(admin_page.locator("tbody")).to_contain_text("123456789")


@pytest.mark.asyncio
async def test_user_add_admin(kamihi: KamihiContainer, admin_page: Page):
    """Test adding a user with admin permissions."""
    kamihi.run_and_wait_for_log(
        "kamihi user add 123456789 --admin", "User added.", "SUCCESS", {"telegram_id": 123456789, "is_admin": True}
    )
    await admin_page.get_by_role("link", name=" Users").click()
    await expect(admin_page.locator("#dt_info")).to_contain_text("Showing 1 to 1 of 1 entries")
    await expect(admin_page.locator("tbody")).to_contain_text("123456789")
    await expect(admin_page.get_by_role("cell", name="").locator("i")).to_be_visible()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "telegram_id",
    [
        "invalid_id",
        "123abc456",
        "1234567890123456789012345678901234567890",  # Too long
    ],
)
async def test_user_add_invalid_telegram_id(kamihi: KamihiContainer, admin_page: Page, telegram_id: str):
    """Test adding a user with an invalid Telegram ID."""
    kamihi.run_and_wait_for_message(
        f"kamihi user add '{telegram_id}'",
        "Invalid value for 'TELEGRAM_ID'",
    )
    await admin_page.get_by_role("link", name=" Users").click()
    await expect(admin_page.locator("#dt_info")).to_contain_text("Showing 0 to 0 of 0 entries")
    await expect(admin_page.locator("tbody")).to_have_count(1)
    await expect(admin_page.locator("tbody")).to_contain_text("No matching records found")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "models_folder",
    [
        {
            "user.py": """\
                from kamihi import bot, BaseUser
                from mongoengine import StringField
                 
                @bot.user_class
                class MyCustomUser(BaseUser):
                    name: str = StringField()
            """,
        }
    ],
)
async def test_user_add_custom_data(kamihi: KamihiContainer, admin_page: Page, models_folder):
    """Test adding a user with custom data."""
    kamihi.run_and_wait_for_log(
        'kamihi user add 123456789 --data \'{"name": "John Doe"}\'',
        "User added",
        "SUCCESS",
        {"telegram_id": 123456789, "is_admin": False, "name": "John Doe"},
    )
    await admin_page.get_by_role("link", name=" My Custom Users").click()
    await expect(admin_page.locator("#dt_info")).to_contain_text("Showing 1 to 1 of 1 entries")
    await expect(admin_page.locator("tbody")).to_contain_text("123456789")
    await expect(admin_page.locator("tbody")).to_contain_text("John Doe")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "models_folder",
    [
        {
            "user.py": """\
                from kamihi import bot, BaseUser
                from mongoengine import StringField

                @bot.user_class
                class MyCustomUser(BaseUser):
                    name: str = StringField()
            """,
        }
    ],
)
@pytest.mark.parametrize(
    "data",
    [
        "invalid_json",
        '{"name": "John Doe"',  # Missing closing brace
    ],
)
async def test_user_add_custom_data_invalid_json_format(
    kamihi: KamihiContainer, admin_page: Page, models_folder, data: str
):
    """Test adding a user with invalid JSON data format."""
    kamihi.run_and_wait_for_message(
        f"kamihi user add 123456789 --data '{data}'",
        "Invalid JSON data",
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "models_folder",
    [
        {
            "user.py": """\
                from kamihi import bot, BaseUser
                from mongoengine import StringField

                @bot.user_class
                class MyCustomUser(BaseUser):
                    name: str = StringField(required=True)
            """,
        }
    ],
)
async def test_user_add_custom_data_missing_required_field(kamihi: KamihiContainer, admin_page: Page, models_folder):
    """Test adding a user with missing required custom data field."""
    kamihi.run_and_wait_for_log("kamihi user add 123456789", "User inputted is not valid.", "ERROR")


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "models_folder",
    [
        {
            "user.py": """\
                from kamihi import bot, BaseUser
                from mongoengine import StringField

                @bot.user_class
                class MyCustomUser(BaseUser):
                    name: str = StringField(required=True)
            """,
        }
    ],
)
async def test_user_add_custom_data_field_not_defined(kamihi: KamihiContainer, admin_page: Page, models_folder):
    """Test adding a user with custom data field not defined in the user model."""
    kamihi.run_and_wait_for_log(
        'kamihi user add 123456789 --data \'{"undefined_field": "value"}\'',
        "Custom user model does not have the field provided.",
        "ERROR",
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "models_folder",
    [
        {
            "user.py": """\
                from kamihi import bot, BaseUser
                from mongoengine import StringField

                @bot.user_class
                class MyCustomUser(BaseUser):
                    name: str = StringField(required=True)
            """,
        }
    ],
)
async def test_user_add_custom_data_invalid_type(kamihi: KamihiContainer, admin_page: Page, models_folder):
    """Test adding a user with custom data of invalid type."""
    kamihi.run_and_wait_for_log(
        "kamihi user add 123456789 --data '{\"name\": 1234567890}'", "User inputted is not valid.", "ERROR"
    )


@pytest.mark.asyncio
async def user_add_existing_user(kamihi: KamihiContainer, user_in_db: dict):
    """Test adding a user that already exists in the database."""
    kamihi.run_and_wait_for_log(f"kamihi user add {user_in_db['telegram_id']}", "User inputted is not valid.", "ERROR")
