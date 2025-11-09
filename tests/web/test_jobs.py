"""
Functional tests for job management.

License:
    MIT
"""
import re

import pytest
from playwright.async_api import Page, expect
from telethon.tl.custom import Conversation

from tests.fixtures.docker_container import KamihiContainer


@pytest.fixture
async def job_page(kamihi: KamihiContainer, page) -> Page:
    """Fixture that provides the job page of the Kamihi web interface."""
    await page.goto(f"http://{kamihi.ips.primary}:4242/job/list")
    return page


@pytest.fixture
def actions_folder():
    return {
        "start/__init__.py": "",
        "start/start.py": """\
            from kamihi import bot
                         
            @bot.action
            async def start():
                return f"Hello there!"
        """,
    }


@pytest.fixture
def config_file():
    return {
        "kamihi.yaml": """\
        jobs:
            enabled: true
    """
    }


@pytest.mark.asyncio
@pytest.mark.parametrize("config_file", [{"kamihi.yaml": ""}])
async def test_job_disabled(job_page: Page, config_file):
    """Test that the job page is not accessible when jobs are disabled."""
    await expect(job_page.locator("body")).to_contain_text("404")
    await expect(job_page.locator("body")).to_contain_text("Oops… You just found an error page")


@pytest.mark.asyncio
async def test_job_create(user, job_page: Page):
    """Test the creation of a job through the web interface."""
    await job_page.get_by_role("link", name="+ New Job").click()
    await job_page.get_by_role("textbox", name="Select action").click()
    await job_page.get_by_role("option", name="name: start").click()
    await job_page.get_by_role("checkbox", name="Enabled").check()
    await job_page.get_by_placeholder("Select users").click()
    await job_page.get_by_text("telegram_id:").click()
    await job_page.get_by_role("textbox", name="Cron expression").click()
    await job_page.get_by_role("textbox", name="Cron expression").fill("* * * */5 *")
    await job_page.get_by_role("button", name="Save", exact=True).click()
    await expect(job_page.locator("tbody")).to_contain_text("/start")
    await expect(job_page.locator("tbody")).to_contain_text(str(user["telegram_id"]))
    await expect(job_page.locator("tbody")).to_contain_text("-empty-")
    await expect(job_page.locator("tbody")).to_contain_text("* * * */5 *")


@pytest.mark.asyncio
async def test_job_create_invalid_cron(user, job_page: Page):
    """Test the creation of a job with an invalid cron expression through the web interface."""
    await job_page.get_by_role("link", name="+ New Job").click()
    await job_page.get_by_role("textbox", name="Select action").click()
    await job_page.get_by_role("option", name="name: start").click()
    await job_page.get_by_role("checkbox", name="Enabled").check()
    await job_page.get_by_placeholder("Select users").click()
    await job_page.get_by_text("telegram_id:").click()
    await job_page.get_by_role("textbox", name="Cron expression").click()
    await job_page.get_by_role("textbox", name="Cron expression").fill("invalid-cron")
    await job_page.get_by_role("button", name="Save", exact=True).click()
    await expect(job_page.locator("form")).to_contain_text("Invalid cron expression.")


@pytest.mark.asyncio
async def test_job_run_manually(user, job_page: Page, chat: Conversation):
    """Test running a job manually through the web interface."""

    await job_page.get_by_role("link", name="+ New Job").click()
    await job_page.get_by_role("textbox", name="Select action").click()
    await job_page.get_by_role("option", name="name: start").click()
    await job_page.get_by_role("checkbox", name="Enabled").check()
    await job_page.get_by_placeholder("Select users").click()
    await job_page.get_by_text("telegram_id:").click()
    await job_page.get_by_role("textbox", name="Cron expression").click()
    await job_page.get_by_role("textbox", name="Cron expression").fill("* * * */5 *")
    await job_page.get_by_role("button", name="Save", exact=True).click()
    await expect(job_page.locator("tbody")).to_contain_text("/start")
    await expect(job_page.locator("tbody")).to_contain_text(str(user["telegram_id"]))
    await expect(job_page.locator("tbody")).to_contain_text("-empty-")
    await expect(job_page.locator("tbody")).to_contain_text("* * * */5 *")

    await chat.send_message("dummy")  # To ensure the conversation exists
    response = await chat.get_response()
    assert response.text == "I'm sorry, but I don't know how to respond to that"

    await job_page.get_by_role("button", name="Actions").click()
    await job_page.get_by_role("link", name=" Run job manually").click()
    await job_page.get_by_role("button", name="Yes, run job").click()
    await expect(job_page.get_by_role("alert")).to_contain_text("Job executed successfully.")

    response = await chat.get_response()

    assert response.text == "Hello there!"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "actions_folder,per_user,expected_response",
    [
        (
            {
                "start/__init__.py": "",
                "start/start.py": """\
                    from kamihi import bot
                    from models.user import User
                                 
                    @bot.action
                    async def start(user: User | None):
                        return f"Hello there, {user.telegram_id}!"
                """,
            },
            True,
            "Hello there, {telegram_id}!",
        ),
        (
            {
                "start/__init__.py": "",
                "start/start.py": """\
                    from kamihi import bot
                    from models.user import User
                                 
                    @bot.action
                    async def start(user: User | None):
                        return f"Hello there, {user}!"
                """,
            },
            False,
            "Hello there, None!",
        ),
        (
            {
                "start/__init__.py": "",
                "start/start.py": """\
                    from kamihi import bot
                    from models.user import User
                                 
                    @bot.action
                    async def start(users: list[User]):
                        return f"My users are {', '.join(str(user.telegram_id) for user in users)}"
                """,
            },
            False,
            "My users are {telegram_id}",
        ),
        (
            {
                "start/__init__.py": "",
                "start/start.py": """\
                    from kamihi import bot
                    from models.user import User
                                 
                    @bot.action
                    async def start(users: list[User]):
                        return f"My users are {', '.join(str(user.telegram_id) for user in users)}"
                """,
            },
            True,
            "My users are {telegram_id}",
        )
    ],
)
async def test_job_per_user(user, job_page: Page, chat: Conversation, actions_folder, per_user, expected_response):
    """Test running a job manually through the web interface."""
    await job_page.get_by_role("link", name="+ New Job").click()
    await job_page.get_by_role("textbox", name="Select action").click()
    await job_page.get_by_role("option", name="name: start").click()
    await job_page.get_by_role("checkbox", name="Enabled").check()

    if per_user:
        await job_page.get_by_role("checkbox", name="Per user").check()

    await job_page.get_by_placeholder("Select users").click()
    await job_page.get_by_text("telegram_id:").click()
    await job_page.get_by_role("textbox", name="Cron expression").click()
    await job_page.get_by_role("textbox", name="Cron expression").fill("* * * */5 *")
    await job_page.get_by_role("button", name="Save", exact=True).click()
    await expect(job_page.locator("tbody")).to_contain_text("/start")
    await expect(job_page.locator("tbody")).to_contain_text(str(user["telegram_id"]))
    await expect(job_page.locator("tbody")).to_contain_text("-empty-")
    await expect(job_page.locator("tbody")).to_contain_text("* * * */5 *")

    await chat.send_message("dummy")  # To ensure the conversation exists
    response = await chat.get_response()
    assert response.text == "I'm sorry, but I don't know how to respond to that"

    await job_page.get_by_role("button", name="Actions").click()
    await job_page.get_by_role("link", name=" Run job manually").click()
    await job_page.get_by_role("button", name="Yes, run job").click()
    await expect(job_page.get_by_role("alert")).to_contain_text("Job executed successfully.")

    response = await chat.get_response()

    assert response.text == expected_response.format(telegram_id=user["telegram_id"])
