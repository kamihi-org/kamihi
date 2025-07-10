This guide explains how to run and develop tests for the Kamihi project, including unit and functional tests.

## Unit testing

Unit tests are located in the `tests/unit` directory. They are organized in the same way as the source code, with a folder per module, each with one or more test files that normally correspond to the files in the module.

Unit tests are written using `pytest`. Once the project has been correctly set up following the [setup guide](setup.md), you just need to install their dependencies and run them:

```bash
$ uv sync --group unit
$ uv run pytest tests/unit
```

## Functional testing

!!! note
    Functional tests make use of automated Docker container deployments, and thus are very resource-intensive. Make sure your machine is powerful enough to handle them.

!!! warning
    As of the time of writing this documentation, it is not possible to run functional tests unless you have an iOS device for the initial setup. This is because for now creating test accounts can only be done through the Telegram app on iOS. This is a limitation of Telegram, not Kamihi.

Functional tests are located in the `tests/functional` directory. They are organized by feature, based loosely on the structure of the source code but not constrained by it.

### Setup

Running functional tests requires a bit more setup, as they run on Telegram's [test accounts](https://core.telegram.org/api/auth#test-accounts) (to avoid bans and FLOOD errors). To create the environment needed for them, you can follow these steps:

1. Install the dependencies:
    ```bash
    $ uv sync --group unit --group func
    ```
2. Make sure you have Docker and Docker Compose installed on your machine.
    ```bash
    $ docker --version
    $ docker compose --version
    ```
3. Create a `.env` file in the root of the project with the following content, which we will fill in as we go along:
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
    $ uv run tests/functional/utils/get_string_session.py
    ```
    This value can then be added to the `.env` file in the `TG_SESSION` variable.
12. Last, but not least, we need a bot to test on. From your test account, talk to the [@BotFather](https://t.me/botfather) and fill in the `BOT_TOKEN` and `BOT_USERNAME` values in the `.env` file.

Once this odyssey has been completed, you should be able to run the functional tests with the following command:

```bash
$ uv run pytest tests/functional
```

### Available fixtures

The functional test suite comes with several convenience fixtures to make writing tests easier:

#### Core testing infrastructure

- **`test_settings`** - Provides `TestingSettings` instance with all configuration values from environment variables and `.env` file.
- **`tg_client`** - Session-scoped Telegram client for interacting with the test bot, automatically connects and disconnects. Ideally, instead of using this fixture, you should use...
- **`chat`** - Opens a conversation with the test bot using the test user, providing a `Conversation` object for sending/receiving messages.

#### Application structure fixtures

These fixtures provide the content of the project under test in the container. All of them are dictionaries where the keys represent the paths of the files and the values represent the contents. Directories get created automatically. You can override them to provide custom content for testing:

- **`pyproject`** - Returns a dictionary with `pyproject.toml` as key and the file content as value.
- **`config_file`** - Returns a dictionary with `kamihi.yml` as key and the file content as value.
- **`actions_folder`** - Dictionary representing the actions folder structure and all its files. Gets `actions/` prepended to all keys at runtime.
- **`models_folder`** - Dictionary representing the models folder structure and all its files. Gets `models/` prepended to all keys at runtime.
- **`app_folder`** - Combines all application files into a single dictionary for container mounting. Not to be overridden unless you know what you're doing.

#### Container and database fixtures

- **`mongo_container`** - MongoDB container instance for database operations.
- **`kamihi_container`** - Custom `KamihiContainer` instance with enhanced logging and control methods.
- **`kamihi`** - Main fixture that ensures the Kamihi container is started and ready for testing. This is the one you should use in your tests to interact with the Kamihi application, unless for some reason you need to use the application before it is fully started, in which case you can use the `kamihi_container` fixture directly.

#### Database fixtures

- **`mongodb`** - MongoDB client connected to the test database using Pymongo, for manually editing the database during tests.

#### User management fixtures

- **`user_custom_data`** - Dictionary for custom user data (empty by default, can be overridden). To be used with the `models_folder` fixture to test with custom user models.
- **`user_in_db`** - Creates a test user using the test user ID in the database and returns the user document.
- **`add_permission_for_user`** - Generator fixture that returns a function to add permissions to users for specific actions.

#### Web interface fixtures

- **`admin_page`** - Provides an asynchronous Playwright `Page` object for the Kamihi admin interface.

#### Content functions

These are not fixtures, you must import them directly from `tests.conftests` and use them as normal functions, not in the test function signature:

- **`random_image()`** - Returns a random image file in bytes format, useful for testing image uploads.
- **`random_video_path()`** - Returns a random video file path from `tests/static/videos`, useful for testing video uploads.
- **`random_audio_path()`** - Returns a random audio file path from `tests/static/audios`, useful for testing audio uploads.
- **`random_voice_note_path()`** - Returns a random voice message file path from `tests/static/audios`, useful for testing voice messages.

#### Utility fixtures

- **`run_command`** - Sets the command for running the bot in the container (`"kamihi run"` by default).
- **`sync_and_run_command`** - UV-wrapped version of the run command. Do not override this unless you know what you're doing, as it will probably make your tests fail.
- **`cleanup`** - Session-scoped fixture that cleans up Docker resources after tests complete.

#### KamihiContainer methods

The `KamihiContainer` class extends the base container with additional methods:

- **`logs(stream=False)`** - Get container logs as a list or stream
- **`parse_log_json(line)`** - Parse JSON log entries from the container
- **`wait_for_log(message, level="INFO", extra_values=None)`** - Wait for specific log entries
- **`wait_for_message(message)`** - Wait for messages without JSON parsing
- **`assert_logged(level, message)`** - Assert that a log entry was sent
- **`wait_until_started()`** - Wait until the container is fully started
- **`run(command)`** - Execute commands in the container
- **`run_and_wait_for_log(command, message)`** - Run command and wait for specific log output
- **`run_and_wait_for_message(command, message)`** - Run command and wait for an specific message, without JSON parsing
- **`stop()`** - Gracefully stop the container

### Using the fixtures

#### Basic test structure

Most functional tests follow this pattern:

```python
@pytest.mark.asyncio
@pytest.mark.usefixtures("kamihi")
async def test_my_feature(user_in_db, add_permission_for_user, chat):
    """Test description."""
    # Setup permissions
    add_permission_for_user(user_in_db, "my_action")
    
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
def run_command():
    """Override to test without full startup."""
    return "sleep infinity"

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
                from kamihi import bot, BaseUser
                from mongoengine import StringField
                 
                @bot.user_class
                class MyCustomUser(BaseUser):
                    name: str = StringField()
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
    kamihi.run_and_wait_for_message(
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
    add_permission_for_user(user_in_db, "greet")
    
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
