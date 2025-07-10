This guide shows how to send multiple messages in a single action.

It is as easy as returning a list of messages from an action. Kamihi will take care of sending each message in the list to the user.

```python
from kamihi import bot

@bot.action
def start() -> list[str]:
    return [
        "Hello, world!",
        "This is the second message.",
        "And this is the third one.",
    ]
```

The list accepts any type that can be sent by its own. For example, you can return a list of `bot.Photo`, `bot.Video`, or even a mix of different types.

For more information on how lists of media files are handled, see the [send media guide](./send-media.md).