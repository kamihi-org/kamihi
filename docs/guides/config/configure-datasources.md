This guide explains how to configure data sources for your Kamihi application. 

## Supported data sources

Kamihi supports various data sources that can be used to fetch and process data. The following data sources are currently supported:

- **SQLite**: A lightweight, file-based SQL database.
- **PostgreSQL**: A powerful, open-source relational database.

You are welcome to contribute new data sources. See the ["Creating a new datasource type"](../../dev/guides/create-datasource.md) guide for more information.

## Configuration basics

Data sources are configured in the `datasources` section of the `KamihiSettings` class. Every data source is defined by a unique name and its type. The type specified determines the rest of the configuration options required for that data source.

=== "kamihi.yaml"

    ```yaml
    datasources:
      # A sample SQLite datasource
      - name: my_sqlite_db
        type: sqlite
        path: data/database.db
      # A sample PostgreSQL datasource
      - name: my_postgres_db
        type: postgres
        host: localhost
        port: 5432
        database: my_database
        user: my_user
        password: my_password
    ```

=== "`.env` file"

    ```env
    KAMIHI_DATASOURCES='[
        {
            "name": "my_sqlite_db",
            "type": "sqlite",
            "path": "data/database.db"
        },
        {
            "name": "my_postgres_db",
            "type": "postgres",
            "host": "localhost",
            "port": 5432,
            "database": "my_database",
            "user": "my_user",
            "password": "my_password"
        }
    ]'
    ```

    !!! info
        Since the `datasources` section is a list, if defined with environment variables, it needs to be represented as a JSON string.

## Configuration values reference

The following table lists the supported data source types and links to their configuration values reference:

| Data Source Type | Configuration values reference                                                                                                  |
|------------------|---------------------------------------------------------------------------------------------------------------------------------|
| SQLite           | [SQLiteDataSourceConfig](/kamihi/reference/kamihi/datasources/sqlite/#kamihi.datasources.sqlite.SQLiteDataSourceConfig)         |
| PostgreSQL       | [PostgresDataSourceConfig](/kamihi/reference/kamihi/datasources/postgres/#kamihi.datasources.postgres.PostgresDataSourceConfig) |
