This guide explains how to run and develop tests for the Kamihi project.

## Functional testing

!!! note
    Functional tests make use of automated Docker container deployments, and thus are very resource-intensive. Make sure your machine is powerful enough to handle them.

!!! warning
    As of the time of writing this documentation, it is not possible to run functional tests unless you have an iOS device for the initial setup. This is because for now creating test accounts can only be done through the Telegram app on iOS. This is a limitation of Telegram, not Kamihi.

Functional tests are located in the `tests` directory. They are organized by feature, based loosely on the structure of the source code but not constrained by it.

### Setup

Running functional tests requires a bit more setup, as they run on Telegram's [test accounts](https://core.telegram.org/api/auth#test-accounts) (to avoid bans and FLOOD errors). To create the environment needed for them, you can follow these steps:

1. Install the dependencies:
    ```bash
    $ uv sync --group tests
    ```
2. Make sure you have Docker and Docker Compose installed on your machine.
    ```bash
    $ docker --version
    $ docker compose --version
    ```
3. Create a `settings.yml` file in the `tests/` folder with the following content, which we will fill in as we go along:
    ```env
    KAMIHI_TESTING__BOT_TOKEN=
    KAMIHI_TESTING__BOT_USERNAME=
    KAMIHI_TESTING__USER_ID=/
    KAMIHI_TESTING__TG_PHONE_NUMBER=/
    KAMIHI_TESTING__TG_API_ID=/
    KAMIHI_TESTING__TG_API_HASH=/
    KAMIHI_TESTING__TG_SESSION=/
    KAMIHI_TESTING__TG_DC_ID=/
    KAMIHI_TESTING__TG_DC_IP=/
    ```
4. Go to your Telegram account's developer panel, sign in with your account, and create a new application.
5. From the 'App configuration' section, you can obtain the values for `TG_API_ID` (App api_id) and `TG_API_HASH` (App api_hash).
6. From the 'Available MTProto Servers' section, you can obtain the values for `TG_DC_IP` (Text field besides 'Test configuration:') and `TG_DC_ID` (Number just below the IP, prepended by 'DC'). Beware that `TG_DC_ID` is just the number, without the 'DC' prefix.
7. You need an account on the test servers so you don't hit limitations or risk a ban on your main account. To create a test account:
    1. Get the Telegram app on iOS, if you don't have it already, and log in with your main account (or with any account, really).
    2. Tap the Settings icon in the bottom bar ten times to access the developer settings.
    3. Select 'Accounts', then 'Login to another account', then 'Test'
    4. Input your phone number (must be a valid number that can receive SMS) and tap 'Next', confirm the phone and input the code you receive via SMS.
8. (optional) You can log in with the test account on the desktop application following this steps:
    1. Go to the sidebar
    2. While holding Alt and Shift, right-click on the 'Add account' button
    3. Select 'Test server'
    4. Log in by scanning the QR code from the Telegram app on iOS that has the test account
9. Once you hace the test account created, you can fill the value for `TG_PHONE_NUMBER` with the one you used for the test account, including international prefix and no spaces or other characters, e.g. +15559786475.
10. Now you must obtain your test account's Telegram User ID. The easiest is to message one of the many bots that will provide it for you, like [this one](https://t.me/myidbot). This value corresponds to the `USER_ID' environment variable.
11. For the tests to be able to log in without any user input, two-factor authentication must be skipped. For that to happen, we need a session token. We have a script for that, so to obtain the token, run the following command from the root of the project after having filled in all the values from the previous steps in the `.env` file:
    ```bash
    $ uv run tests/utils/get_string_session.py
    ```
    This value can then be added to the `.env` file in the `TG_SESSION` variable.
12. Last, but not least, we need a bot to test on. From your test account, talk to the [@BotFather](https://t.me/botfather) and fill in the `BOT_TOKEN` and `BOT_USERNAME` values in the `.env` file.

Once this odyssey has been completed, you should be able to run the functional tests with the following command:

```bash
$ uv run pytest
```

### Available fixtures

The functional test suite provides fixtures grouped by module:

#### Container management fixtures (`tests.fixtures.docker_container`)

- `db_url`: Database URL used by the container (defaults to `sqlite:///./kamihi.db`). For ad‑hoc queries, use `kamihi_container.query_db(sql)`.
- `kamihi_container`: Custom KamihiContainer with enhanced logging and helper methods:
    - `command_logs: list[str]`: In‑memory chronological log of every command executed and every line observed while waiting for logs; printed automatically on test failure.
    - `EndOfLogsException`: Raised by waiting helpers if the log stream ends before the expected entry is found.
    - `parse_log_json(line: str) -> dict | None`: Parse a structured (JSON‑serialized) log line. Ensures required keys exist; returns dict or None if invalid.
    - `wait_for_log(stream, message, level="INFO", extra_values: dict[str, Any] | None = None, parse_json: bool = True) -> dict | str`: Consume a Docker log stream until a line matches. If `parse_json` is True, matches on structured log record (level + substring in message + optional key/value pairs inside `record.extra`). If `parse_json` is False, performs a plain substring match and returns the raw line.
    - `wait_for_message(message: str, stream=None) -> str`: Convenience wrapper for plain‑text (non‑JSON) message search.
    - `run_command(command: str) -> CancellableStream`: Execute a command inside the container (`docker exec`) and return the live output stream (bytes iterator). Also appends `$ <command>` to `command_logs`.
    - `run_command_and_wait_for_log(command, message, level="INFO", extra_values=None, parse_json=True) -> dict | str`: Fire a command then immediately wait for a matching log/message (delegates to the two helpers above).
    - `run_command_and_wait_for_message(command, message) -> str`: Plain‑text variant of the previous helper.
    - `uv_sync(command: str = "uv sync") -> None`: Runs dependency sync.
    - `db_migrate(command: str = "kamihi db migrate") -> None`: Applies migrations; waits for structured log containing `Migrated` at `SUCCESS` level.
    - `db_upgrade(command: str = "kamihi db upgrade") -> None`: Applies any pending schema upgrades; waits for `Upgraded` at `SUCCESS` level.
    - `start(command: str = "kamihi run") -> None`: Starts the Kamihi app; waits for `Started!` at `SUCCESS` level.
    - `stop() -> None`: Terminates the running process with `SIGKILL` (fast, deterministic teardown for tests).
    - `query_db(sql: str) -> list[tuple]`: Copies the SQLite DB file out of the container to a temp file and executes a read query; returns rows. (Write statements are not intended; treat as read‑only.)
- `kamihi`: Ensures the container is synced, migrated, upgraded, started, and properly stopped around each test. This is the main fixture to use in tests (instead of `kamihi_container`, which should be used only if lifecycle control is needed).
- `cleanup`: Session‑scoped, autouse; prunes containers, volumes, and images after the session and prints a summary.

#### Docker-mountable app files fixtures (`tests.fixtures.docker_files`)

These fixtures provide the content mounted into the container. All return dictionaries where keys are file paths and values are file contents. Directories are created automatically. Override them to provide custom content:

- `pyproject_extra_dependencies`: Extra dependency list injected into pyproject.toml. Override to add dependencies.
- `pyproject`: {"pyproject.toml": "..."} including kamihi as dependency and Alembic config. Override to change project configuration, but be sure to include the original content to avoid problems.
- `config_file`: {"kamihi.yaml": "..."}. Override to change kamihi configuration.
- `actions_folder`: Dict representing actions; keys relative to actions/. Override to provide custom actions.
- `models_folder`: Dict representing models; keys relative to models/. Override to provide custom models.
- `migrations_folder`: Dict representing Alembic migrations; keys relative to migrations/. Don't override unless you know what you're doing.
- `app_folder`: Combines all the above for container mounting. Do not override unless necessary.

#### App utilities and commands (`tests.fixtures.app`)

- `admin_page`: Async Playwright Page for the Kamihi admin interface. 
- `user_custom_data`: Dict for custom user data (empty by default). Override to provide custom data to add in `user`.
- `user`: Creates a user with the configured test user_id; yields the created user details.
- `add_permission_for_user`: Yields a function to add a permission to a user for a specific action.
- `add_role`: Yields a function to create a role.
- `assign_role_to_user`: Yields a function to assign an existing role to a user.

#### Telegram client fixtures (`tests.fixtures.tg`)

- `tg_client`: Session‑scoped Telethon client using test settings and test DC. Don't use directly; use `chat` instead.
- `chat`: Session‑scoped Conversation opened with the test bot.

#### Testing settings (`tests.fixtures.settings`)

- `test_settings`: Provides a TestingSettings instance populated from environment variables (`KAMIHI_TESTING__*`).

### Using the fixtures

#### Basic test structure

Most functional tests follow this pattern:

```python
@pytest.mark.asyncio
@pytest.mark.usefixtures("kamihi")
async def test_my_feature(user_in_db, add_permission_for_user, chat):
    """Test description."""
    # Setup permissions
    add_permission_for_user(user_in_db["telegram_id"], "my_action")
    
    # Test interaction
    await chat.send_message("/my_command")
    response = await chat.get_response()
    
    # Assertions
    assert response.text == "expected response"
```

#### Overriding fixtures

##### File-level overrides

Override fixtures for an entire test file by redefining the fixture:

```python
@pytest.fixture
def actions_folder():
    """Custom actions for all tests in this file."""
    return {
        "start/__init__.py": "",
        "start/start.py": """\
            from kamihi import bot
            
            @bot.action
            async def start():
                return "Hello World!"
        """,
    }

def test_my_feature(kamihi, chat):
    # All tests in this file use the overridden fixtures
    pass
```

##### Function-level overrides

Override fixtures for specific tests by decorating individual functions:

```python
@pytest.mark.parametrize("user_custom_data", [{"name": "John Doe"}])
@pytest.mark.parametrize(
    "models_folder",
    [
        {
            "user.py": """\
                from kamihi.db import BaseUser
                from sqlalchemy import Column, String
                
                class User(BaseUser):
                    __table_args__ = {'extend_existing': True}
                    name = Column(String, nullable=True)
            """,
        }
    ],
)
async def test_custom_user_model(user_in_db, chat, models_folder):
    # This test uses custom user model and data
    pass
```

#### Common patterns

##### Using test media files

You can use the provided utility functions to add media files to your tests:

```python
@pytest.mark.asyncio
@pytest.mark.usefixtures("kamihi")
@pytest.mark.parametrize(
    "actions_folder",
    [
        (
            {
                "start/__init__.py": "",
                "start/start.py": """\
                    from pathlib import Path
                    from kamihi import bot
                
                    @bot.action
                    async def start() -> list[bot.Photo]:
                        return [
                            bot.Photo(Path("actions/start/image.jpg")),
                            bot.Video(Path("actions/start/video.mp4")),
                            bot.Audio(Path("actions/start/audio.mp3")),
                            bot.Voice(Path("actions/start/audio.m4a")),
                        ]
                """,
                "start/image.jpg": random_image(),
                "start/video.mp4": random_video_path().read_bytes(),
                "start/audio.mp3": random_audio_path().read_bytes(),
                "start/audio.m4a": random_voice_note_path().read_bytes(),
            },
        ),
    ]
)
async def test(..., actions_folder): ...
```


##### Testing CLI commands

```python
def test_cli_validation(kamihi):
    """Test invalid CLI parameters."""
    kamihi.run_command_and_wait_for_message(
        "kamihi run --port=invalid",
        "Invalid value for '--port'"
    )
```

If testing the `kamihi run` command, you can override the `run_command` fixture to avoid starting the application twice, which will generate conflicts:

```python
@pytest.fixture
def run_command():
    """Override to test CLI without full application startup."""
    return "sleep infinity"
```

##### Testing web interface

```python
@pytest.mark.asyncio
async def test_web_feature(admin_page):
    """Test admin interface functionality."""
    await admin_page.get_by_role("link", name="Users").click()
    await admin_page.get_by_role("button", name="+ New User").click()
    # Continue with Playwright interactions
```

##### Testing bot actions with custom code

```python
@pytest.mark.parametrize(
    "actions_folder",
    [
        {
            "greet/__init__.py": "",
            "greet/greet.py": """\
                from kamihi import bot
                
                @bot.action
                async def greet(user):
                    return f"Hello {user.telegram_id}!"
            """,
        }
    ],
)
async def test_greeting(user_in_db, add_permission_for_user, chat, actions_folder):
    """Test custom greeting action."""
    add_permission_for_user(user_in_db["telegram_id"], "greet")
    
    await chat.send_message("/greet")
    response = await chat.get_response()
    
    assert str(user_in_db['telegram_id']) in response.text
```

### Best practices

- **Use `@pytest.mark.usefixtures("kamihi")`** when you need the container running but don't directly interact with it
- **Always add permissions** before testing bot actions using `add_permission_for_user`, otherwise the bot will respond with the default message.
- **Use `dedent()`** for multiline code strings to maintain readable indentation
- **Override `run_command`** to `"sleep infinity"` when testing CLI without full application startup
- **Parametrize at file level** when multiple tests need the same overrides
- **Do not use test classes**; functional tests should be simple functions
- **Use meaningful test descriptions** that explain the specific scenario being tested
- **Use `wait_for_log`** with specific log levels, messages and extra dictionary contents, if there should be any.

## Unit testing

Unit tests are currently not implemented. They may be added in the future, although with the current architecture of the project, they would be highly complex to set up and maintain, and thus not worth the effort.
