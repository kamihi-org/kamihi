This guide details all the parameters that can be included in an action's signature and that will be automatically populated by Kamihi when the action is invoked. These parameters are also included in the template context when using message or query templates.

## Simple parameters

- `user: models.User`: The user who invoked the action. In the case of scheduled actions, this will be `None` if the `per_user` configuration option is not set (see [here](../../guides/jobs/schedule.md#the-per_user-option) for more details).
- `users: list[models.User]`: The list of users that can use the action. In the case of scheduled actions, this will contain all the users selected in the job definition.
- `logger: loguru.Logger`: A logger instance bound to the action context. You can use this logger to log messages related to the action execution. See the [Loguru documentation](https://loguru.readthedocs.io/en/stable/) for more details on how to use it.
- `action_folder: pathlib.Path`: The path to the action's folder. This can be useful if you need to access additional files or resources related to the action.
- `templates: dict[str, jinja2.Template]`: A dictionary containing all the Jinja templates associated with the action. The keys in the dictionary correspond to the template names (e.g., `<template_name>` for a file named `<template_name>.<extension>.jinja`), and the values are the corresponding Jinja `Template` objects.

## Dynamic parameters

- `template: jinja2.Template | Annotated[jinja2.Template, "<template_filename"]`: A Jinja template associated with the action. See the [templates guide](../../guides/actions/use-templates.md) for more details.
- `data: list[Any]`: The result of the SQL query associated with the action. This parameter is available when the action has a query defined (e.g., `<action_name>.<datasource_name>.sql`). The `data` parameter will contain the rows returned by the query as a list of dictionaries, where each dictionary represents a row with column names as keys. See the [queries guide](../../guides/actions/use-datasources.md) for more details.
- `data_*: list[Any]`: The result of any additional SQL queries associated with the action. The `*` in the parameter name corresponds to the name of the datasource used in the query file (e.g., `<action_name>.<datasource_name>.sql` would be available as `data_<datasource_name>`). See the [queries guide](../../guides/actions/use-datasources.md) for more details.

## Advanced parameters

- `update: telegram.Update`: The original `python-telegram-bot` update that triggered the action. This parameter provides access to the full update object, allowing you to extract additional information or perform more complex operations based on the update data. See the [python-telegram-bot documentation](https://python-telegram-bot.readthedocs.io/en/stable/) for more details on the `Update` class and its properties.
- `context: telegram.ext.CallbackContext`: The original `python-telegram-bot` callback context associated with the action. This parameter provides access to the context object, which contains information about the current state of the bot and allows you to manage user data, chat data, and other context-specific information. See the [python-telegram-bot documentation](https://python-telegram-bot.readthedocs.io/en/stable/) for more details on the `CallbackContext` class and its properties.

## Any other parameter

Any other parameter defined in the action's signature that is not listed above will be checked for an Annotated type with a question type. If found, Kamihi will use that question type to ask the user for input when the action is invoked. See the [questions guide](../../guides/actions/ask-questions.md) for more details on how to use question types in actions.

If no matching parameter is found, Kamihi will fill the parameter with `None` and log a warning message.
