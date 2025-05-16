## Unit testing

Unit tests are located in the `tests/unit` directory. They are organized in the same way as the source code, with a folder per module, each with one or more test files that normally correspond to the files in the module.

Unit tests are written using `pytest`, and once the project has been correctly set up, they can be run with the following command:

```bash
$ uv run pytest tests/unit
```

## Functional testing

!!! note
    Functional tests make use of automated Docker container deployments, and thus are very resource-intensive. Make sure your machine is powerful enough to handle them.

!!! warning
    As of the time of writing this documentation, it is not possible to run functional tests unless you have an iOS device for the initial setup. This is because for now creating test accounts can only be done through the Telegram app on iOS. This is a limitation of Telegram, not Kamihi.

Functional tests are located in the `tests/functional` directory. They are organized by feature, based loosely on the structure of the source code but not constrained by it.

Running functional tests requires a bit more setup, as they run on Telegram's [test accounts](https://core.telegram.org/api/auth#test-accounts) (to avoid bans and FLOOD errors). To create the environment needed for them, you can follow these steps:

1. Make sure you have Docker and Docker Compose installed on your machine.
    ```bash
    $ docker --version
    $ docker compose --version
    ```
2. Create a `.env` file in the root of the project with the following content, which we will fill in as we go along:
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
3. Go to your Telegram account's developer panel, sign in with your account, and create a new application.
4. From the 'App configuration' section, you can obtain the values for `TG_API_ID` (App api_id) and `TG_API_HASH` (App api_hash).
5. From the 'Available MTProto Servers' section, you can obtain the values for `TG_DC_IP` (Text field besides 'Test configuration:') and `TG_DC_ID` (Number just below the IP, prepended by 'DC'). Beware that `TG_DC_ID` is just the number, without the 'DC' prefix.
6. You need an account on the test servers so you don't hit limitations or risk a ban on your main account. To create a test account:
    1. Get the Telegram app on iOS, if you don't have it already, and log in with your main account (or with any account, really).
    2. Tap the Settings icon in the bottom bar ten times to access the developer settings.
    3. Select 'Accounts', then 'Login to another account', then 'Test'
    4. Input your phone number (must be a valid number that can receive SMS) and tap 'Next', confirm the phone and input the code you receive via SMS.
7. (optional) You can log in with the test account on the desktop application following this steps:
    1. Go to the sidebar
    2. While holding Alt and Shift, right-click on the 'Add account' button
    3. Select 'Test server'
    4. Log in by scanning the QR code from the Telegram app on iOS that has the test account
8. Once you hace the test account created, you can fill the value for `TG_PHONE_NUMBER` with the one you used for the test account, including international prefix and no spaces or other characters, e.g. +15559786475.
9. Now you must obtain your test account's Telegram User ID. The easiest is to message one of the many bots that will provide it for you, like [this one](https://t.me/myidbot). This value corresponds to the `USER_ID' environment variable.
10. For the tests to be able to log in without any user input, two-factor authentication must be skipped. For that to happen, we need a session token. We have a script for that, so to obtain the token, run the following command from the root of the project after having filled in all the values from the previous steps in the `.env` file:
    ```bash
    $ uv run tests/functional/utils/get_string_session.py
    ```
    This value can then be added to the `.env` file in the `TG_SESSION` variable.
11. Last, but not least, we need a bot to test on. From your test account, talk to the [@BotFather](https://t.me/botfather) and fill in the `BOT_TOKEN` and `BOT_USERNAME` values in the `.env` file.

Once this odyssey has been completed, you should be able to run the functional tests with the following command:

```bash
$ uv run pytest tests/functional
```
