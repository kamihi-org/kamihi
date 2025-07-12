In the [previous tutorial](your-first-bot.md), we got our first bot up and running, but at the moment it doesn't do much.

We can easily add functionality to our bot by adding new actions.

## What are actions?

Actions are the basic units that compose a bot. Each action defines a functionality, and is normally associated with one command (like `/start`, always prefixed with a slash). By adding actions to our bot, we can make it do anything we may want.

## The default action

Your basic bot already comes with an action, and the good news is that you have already used it! By sending the command `/start` to the bot, you executed the action `start`, that lives in the folder `actions/start`. Pretty straightforward, right?

If you open the file `actions/start/start.py`, you will find the following content:

```python
"""
Start action for hello-world.
"""

from kamihi import bot # (1)!


@bot.action # (2)!
async def start() -> str: # (3)!
    """
    Start action for the bot.

    This function is called when the bot starts.
    """
    return f"Hello, I'm your friendly bot. How can I help you today?" # (4)!

```

1. To interact with Kamihi, we import the `bot` object. There is no need to initialize any class, the framework takes care of that.
2. We register an action by decorating any `async` function with `@bot.action`.
3. Although not strictly needed for basic cases, Kamihi works better when the code is typed.
4. The result returned from the decorated function will be sent to the user.

## Creating a new action

The default action is OK, but really basic. It's all right, though, because we can easily add new actions with a simple command:

<!-- termynal -->
```shell
> kamihi action new time

Copying from template version x.x.x
 identical  actions
    create  actions/time
    create  actions/time/time.py
    create  actions/time/__init__.py

```

This command creates a new `actions/time` folder with all the files you need to get this action up and running.

## Making the action interesting

If you start the bot right now, and send the command `/time`, it will answer with a simple "Hello, world!". I think we can do better. Since the command is `/time`, we can make our bot return the time. For that, edit the file `actions/time/time.py` with the following content:

```python
"""
time action.
"""


from datetime import datetime # (1)!

from kamihi import bot


@bot.action
async def time() -> str:
    """
    time action.
    
    Returns:#
        str: The result of the action.

    """
    # Your action logic here
    return (datetime
            .now(bot.settings.timezone_obj) # (2)!
            .strftime("It's %H:%M:%S on %A, %B %d, %Y") # (3)!
            )
```

1. `datetime` is the Python standard library time utility.
2. We can access all the settings of the bot with the `bot.settings` attribute. The `timezone_obj` property gives us a timezone object from the string we set in `kamihi.yml`.
3. To get a nice message, we use this expression to format the date and time.

## Using our new command

We can restart the bot and our new action will automatically get picked up, its command registered in the bot's menu in Telegram.

![The bot's menu](../images/tutorials-adding-actions-menu.png)

And we can use it in the same way as the other one, by sending `/time` to our bot.

## Configuring the timezone

If you live around the Greenwich Meridian, you are all set! Continue to the next section. 

If not, the bot will have told you the wrong time. That is OK, the bot thinks itself in England, but we can easily change that. Refer to [this guide](../guides/config/configure-timezone.md) for information on how to do so, and then come back.

## Recap

We have learned how to create new actions for the bot by using the `kamihi action new <name>` command. We have also learned how to access the bot's settings.

In the actions you create, you can return any Markdown content. You can also integrate it with any other library, as seen with the `time` action, so go wild!

## What's next?

Now that you have a basic bot up and running, and you know how to add actions to it, you can customize it to your heart's content. We have just scratched the surface of what you can do with Kamihi. Check out all the [guides](../guides/index.md) for more in-depth information on how to use Kamihi to the fullest.
