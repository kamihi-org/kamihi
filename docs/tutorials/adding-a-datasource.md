In this tutorial, you will connect your movie rentals bot to the Sakila database as datasource. You will learn how to configure the datasource and build simple actions that browse the film catalog.

By the end of this tutorial, you will have actions that can list films from Sakila.

## Prerequisites

To follow along, you will need a copy of the [Sakila database](https://dev.mysql.com/doc/sakila/en/) in SQLite version. Please download a copy from [here](https://github.com/bradleygrant/sakila-sqlite3/blob/main/sakila_master.db?raw=true) and save it to the root of your Kamihi project as `sakila.db`.

## What is Sakila?

Sakila is a sample database provided by MySQL that represents a DVD rental store. It includes tables for films, actors, customers, rentals, and stores. We will be using mainly the film catalog tables for this tutorial.

## What is a datasource in Kamihi?

A datasource in Kamihi is a connection to an external database that allows your bot to read data. Datasources can be configured in the `kamihi.yaml` file or via environment variables, and can be used in your actions to run SQL queries.

??? info "What is the difference between a datasource and Kamihi's built-in database?"
    Kamihi's built-in database is used to store bot-specific data such as users, roles, and permissions. Datasources, on the other hand, are external databases that your bot can connect to for reading application-specific data, such as the Sakila film catalog.

## Installing dependencies

Datasources require specific database drivers to work. To work with SQLite datasources, you need to install Kamihi with the option `sqlite`. Run the following command in your terminal:

<!-- termynal -->
```bash
> uv add kamihi[sqlite]
Resolved 76 packages in 58ms
Installed 1 package in 5ms
 + aiosqlite==0.21.0
```

## Configuring the Sakila datasource

To configure the Sakila datasource, you need to add the following to your `kamihi.yaml` file:

```yaml
datasources:
  - type: sqlite
    name: sakila
    path: sakila.db
```

## Creating a new action that uses the datasource

You can probably remember from the previous tutorial how to create a new action. Let's create an action called `catalog` that will contain our film listing and details actions. Run the following command:

<!-- termynal -->
```shell
> kamihi action new catalog

Copying from template version x.x.x
 identical  actions
    create  actions/catalog
    create  actions/catalog/catalog.py
    create  actions/catalog/__init__.py

```

The command will create a new folder `actions/catalog` with the necessary files for a simple action, but now we will go a step further by adding a datasource query file too. Create a new file called `catalog.sakila.sql` under the `actions/catalog` folder with the following content:

=== "`actions/catalog/catalog.sakila.sql`"
    ```sql
    SELECT film_id, title, description, length, rating
    FROM film
    ORDER BY title
    LIMIT 10; -- (1)!
    ```

    1. We will select only the first 10 films for now. In the next tutorial we will learn how to implement pagination to browse through the entire catalog.

??? info "Naming convention for datasource query files"
    The naming convention for datasource query files is `<action_name>.<datasource_name>.sql`. This allows Kamihi to associate the SQL file with the correct action and datasource.

Now we can create a simple action that uses this query to list films from the Sakila database.

=== "`actions/catalog/catalog.py`"
    ```python
    """
    catalog action.
    """
    from kamihi import bot
    
    @bot.action
    async def catalog(data: list) -> str: # (1)!
        """
        List movies from the Sakila database.
        """
        movie_list = "\n".join(f"- {movie.title}" for movie in data) # (2)!
        return f"Available Movies:\n{movie_list}"
    
    ```

    1. The `data` parameter is automatically populated by Kamihi with the results of the SQL query defined in the file with the name `<action_name>.<datasource_name>.sql`, thus the file name format we used earlier. There are, however, other ways to name your files and parameters, which you can check out in the [datasource guide](../guides/actions/use-datasources.md).
    2. `data` is a list of rows returned by the query, where each row is represented as a dictionary-like object. You can access the columns using dot notation (`movie.title`), dictionary keys (`movie["title"]`, or indexing (`movie[1]`).

## TL;DR

- Datasources allow your bot to connect to external databases.
- You can configure datasources in the `kamihi.yaml` file.
- Datasource query files normally follow the naming convention `<action_name>.<datasource_name>.sql`, and are located in the action folder.
- Actions can receive query results as parameters.

## What's next?

In the next tutorial, we will learn how to use templates and pagination to improve the formatting of your messages. You will also create another action that shows detailed information about a selected movie from the Sakila database. Stay tuned!
