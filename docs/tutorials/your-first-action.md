In this tutorial, you will create your first real action for the movie rentals bot. We will focus on understanding how actions work and how to see your action in the admin web interface.

By the end of this tutorial, you will have a new action that tells the current time when you send the `/time` command to your bot.

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

The default action is OK, but useless. It's all right, though, because we can easily add new actions with a simple command:

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

!!! warning "Do not delete the `start` action"
    The `start` action is required by Telegram for the bot to work properly. You can modify it as you like, but do not delete it.

## Making the action do something

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
    return datetime.now().strftime("It's %H:%M:%S on %A, %B %d, %Y") # (2)!
```

1. `datetime` is the Python standard library time utility.
2. To get a nice message, we use this expression to format the date and time.

## Using our new command

We can restart the bot and our new action will automatically get picked up, its command registered in the bot's menu in Telegram.

![The bot's menu](../images/tutorials-adding-actions-menu.png)

And we can use it in the same way as the other one, by sending `/time` to our bot.

## Seeing the action in the admin web interface

One of the great features of Kamihi is the admin web interface, that allows us to see and manage our bot's data. If you open your browser and go to `http://localhost:4242`, you will see the admin interface. By clicking on "Actions" in the sidebar, you will see a list of all the actions registered in your bot, including the new `time` action we just created.

While you are there, you can also check out the "Users", "Roles" and "Permissions" sections, that will help you manage your bot's users and their access levels. We will cover these topics in more detail in later tutorials.

## TL;DR

- Actions are the building blocks of a Kamihi bot.
- You can create new actions using the `kamihi action new <action_name>` command.
- Actions are defined as `async` functions decorated with `@bot.action`.
- You can see and manage your bot's actions in the admin web interface.

## What's next?

The `/time` action we just created is a simple example, but has little to do with movie rentals. In the [next tutorial](adding-a-datasource.md), we will create an action that allows users to browse and rent movies from our bot by connecting to a database.
