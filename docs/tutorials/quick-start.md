## Getting your token

To create a bot, you need a token. This token is a unique identifier for your bot and is used to authenticate it
with the Telegram API. You can get your token by talking to [@BotFather](https://t.me/botfather) on Telegram. Just
send him the `/newbot` command and follow the instructions. He'll give you a token that looks like this:
`123456789:ABC-DEF1234ghIkl-zyx57W2P0s`.

## Creating the bot

You can create your first bot in three lines. No, really! Just three lines. Here's how:

```python
from kamihi import bot

bot.settings.token = "123456789:ABC-DEF1234ghIkl-zyx57W2P0s"

bot.start()
```

Just replace the token with the one you got from BotFather. That's it! You've created your first bot.

## Running the bot

To run the bot, just execute the script. You can do this in your terminal or command prompt. Just navigate to the
directory where you saved the script and run:

```sh
python your_script.py
```

## Making the bot do something

Right now, your bot doesn't do anything other that apologize for not being able to do anything. We can change this
by making our first action. Let's make the bot respond to the `/start` command with a friendly message. Here's how:

```python
from kamihi import bot

bot.settings.token = "123456789:ABC-DEF1234ghIkl-zyx57W2P0s"

@bot.action
async def start():
    return "Hello! I'm your friendly bot. How can I help you today?"

bot.start()
```

You can restart the bot and send the `/start` command to it. The bot will respond with the message you return in the
`start` action.

## Configuring the bot

Having the token hardcoded in your script is not good practice. You can instead use environment variables, an
environment variable file or a configuration file to store this and any other configuration options:

=== "Configuration file"
    Create a file named `kamihi.yaml` in the same directory as your script with the following content:
    ```yaml
    token: "123456789:ABC-DEF1234ghIkl-zyx57W2P0s"
    ```

=== "`.env` file"
    Create a file named `.env` in the same directory as your script with the following content:
    ```dotenv
    KAMIHI_TOKEN="123456789:ABC-DEF1234ghIkl-zyx57W2P0s"
    ```

=== "Environment variables"
    Set the environment variable in the same terminal session where you run the script:
    ```bash
    export KAMIHI_TOKEN="123456789:ABC-DEF1234ghIkl-zyx57W2P0s"
    ```

In your script, just remove the token from the `bot.start()` call:
```python
from kamihi import bot

@bot.action
async def start():
    return "Hello! I'm your friendly bot. How can I help you today?"

bot.start()
```

The bot will automatically read the token from the configuration file, `.env` file or environment variable and use it.

## What now?

Now that you have a basic bot up and running, you can start adding more actions and features to it. We have just
scratched the surface of what you can do with Kamihi. Check out
the [guides](https://kamihi-dev.github.io/kamihi/guides/)
for more in-depth information on how to use Kamihi and its features.
