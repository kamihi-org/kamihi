This guide explains how command names are assigned from actions and how to customize them.

## Default command

When decorating a function to turn it into an action, the command will be **the name of the function**. For example:

```python
from kamihi import bot

@bot.action
async def test() -> str:
    return "Test successful!"
```

This code will register the command `/test` on Telegram.

## Changing the default command

Sometimes we do not want to use the name of the function name as our command. We can easily change it by passing the command we want to the decorator:

```python
from kamihi import bot

@bot.action("hello")
async def test() -> str:
    return "Test successful!"
```

This will register the command `/hello` instead of the command `/test` in Telegram.

## Assigning multiple commands

Extending the previous example, we can easily assign multiple commands to an action by passing them to the decorator:

```python
from kamihi import bot

@bot.action("hello", "hola", "allo")
async def test() -> str:
    return "Test successful!"
```

With this code, all three commands will be registered in Telegram and all will execute the same function `test()`. 

!!! info
    In this case the function name will _not_ be registered as a command.
