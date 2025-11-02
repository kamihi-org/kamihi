This guide explains how to use questions to obtain data from users with your bot.

## Asking questions

To ask a question to a user, add a new parameter to your action and annotate it with a type from `kamihi.questions`. For example:

```python
from kamihi import bot
from kamihi.questions import String
from typing import Annotated

@bot.action
async def greet_user(
        name: Annotated[ # (1)!
            str, # (2)!
            String("What is your name?") # (3)!
        ]
) -> str:
    return f"Hello, {name}!"
```

1. With Annotated we can add metadata to the parameter `name`.
2. We specify that the type of `name` will be `str`.
3. We use the `String` question type to ask the user for their name.

When the user executes the command `/greet_user`, the bot will ask "What is your name?". Once the user responds, the bot will greet them with their name.

## Available question types

Kamihi provides several base question types to handle different kinds of user input:

- `String`: Asks for a text input. Can include optional validation for length or regex patterns.
- `Integer`: Asks for an integer input. Can include optional validation for range or multiples.
- `Boolean`: Asks for a yes/no input. The responses accepted as "yes" or "no" can be customized.
- `Choice`: Asks the user to select from a list of options. Can be presented as a custom keyboard or as inline buttons for easier selection.
- `DynamicChoice`: Similar to `Choice`, but the options are generated dynamically from a request to a datasource.
- `Datetime`, `Date`, `Time`: Asks for date and/or time input. Can include optional validation for ranges or past/future dates, and can parse various formats by using the library [`dateparser`](https://dateparser.readthedocs.io/en/latest/).
- `File`: Asks the user to upload a file. Can specify allowed file types and maximum file size.
- `Image`: Asks the user to upload an image. Can specify allowed image formats, maximum dimensions, and file size.

To use these question types, simply import them from `kamihi.questions` and annotate your action parameters as shown in the example above. Consult the [API reference](../../reference/kamihi/questions/index.md) for detailed information on each question type and their available options.

!!! info "A note on using `DynamicQuestion`"
    When using `DynamicQuestion`, a path to a request file has to be specified. The file name should follow the same rules described in [the guide on data sources](./use-datasources.md#writing-queries). If the path specified is relative, it will be assumed to be relative to a folder `questions` in the root of the project.

