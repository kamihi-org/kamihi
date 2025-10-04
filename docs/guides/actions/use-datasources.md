This guide explains how to use data sources in your actions. Data sources allow you to fetch and process data from various sources, such as databases, and use that data to compose responses or perform actions in your Kamihi bot.

To use datasources in your actions, you must have first configured them. See the [Configure datasources guide](../config/configure-datasources.md) for more information on how to perform this set up.

## Writing queries

Data sources will fetch and execute SQL queries defined in your actions, and put the results in your action's arguments for you to use.

After writing your query in the appropriate SQL dialect for the datasource, save it in the action directory using the following naming convention:

```
<query_name>.<datasource_name>.sql
```

For actions that have one query, it is recommended that the query name be the same as the action name. For example, for an action named `get_users` that uses a datasource named `my_sqlite_db`, you should name the file `get_users.my_sqlite_db.sql`.

## Using the data in your action

There are three main patterns for using data from data sources in your actions:

1. **Implicit**: Automatically selects the query based on the action name.
2. **By argument name**: Uses a specific naming convention to match query results to action arguments.
3. **Explicit**: Uses the `Annotated` type to specify which query corresponds to which argument.

You can choose the pattern that best fits your use case, and you can mix and match these patterns in your actions as needed.

### Implicit

You define the function argument `data` in your action, and Kamihi will automatically select the appropriate query and datasource based on the query file name.

Continuing from the previous example, if you have a file named `get_users.my_sqlite_db.sql` in the `get_users` action folder, you can define your action like this:

```python
from kamihi import bot

@bot.action
async def get_users(data: list[dict]):
    # The data argument will contain the results of the query
    for user in data:
        print(f"User: {user['name']}, Email: {user['email']}")
```

The `data` argument will automatically be populated with the results of the query defined in `get_users.my_sqlite_db.sql`.

!!! warning
    This pattern only works when there is only one query in the action folder and the query name is the same as the action name (`<action_name>.<datasource_name>.sql`). 

    If you have multiple queries in the same action, you will need to use one of the other patterns described below.

### By argument name

When having multiple queries in the same action, you can specify which query corresponds to which argument by using the following argument name convention:

```
data_<query_name>
```

For example, if you have an action `get_users` with two queries, `normal_users.my_sqlite_db.sql` and `premium_users.my_postgres_db.sql`, you can define your action like this:

```python
from kamihi import bot

@bot.action
async def get_users(data_normal_users: list[dict], data_premium_users: list[dict]):
    # The data_normal_users argument will contain the results of the normal users query
    for user in data_normal_users:
        print(f"Normal User: {user['name']}, Email: {user['email']}")

    # The data_premium_users argument will contain the results of the premium users query
    for user in data_premium_users:
        print(f"Premium User: {user['name']}, Email: {user['email']}")
```

### Explicit

Finally, you can also specify explicitly the query to insert in an argument by using Annotated. This pattern gives you total freedom to name your arguments however you want.

```python
from kamihi import bot
from typing import Annotated

@bot.action
async def get_users(
    normal_users: Annotated[list[dict], "normal_users.my_sqlite_db.sql"],
    premium_users: Annotated[list[dict], "premium_users.my_postgres_db.sql"]
):
    # The normal_users argument will contain the results of the normal users query
    for user in normal_users:
        print(f"Normal User: {user['name']}, Email: {user['email']}")

    # The premium_users argument will contain the results of the premium users query
    for user in premium_users:
        print(f"Premium User: {user['name']}, Email: {user['email']}")
```
