This guide will show the steps to set up different DBMS for your Kamihi project. 

By default, Kamihi uses SQLite, which is a serverless, self-contained database engine. However, for production environments or more complex applications, you might want to use a more robust DBMS like PostgreSQL or MySQL.

## Supported DBMS

For now, Kamihi supports the following DBMS:

- SQLite
- PostgreSQL

If you need support for another DBMS, please open an issue on our [issue tracker](https://github.com/kamihi-org/kamihi/issues).

## SQLite

SQLite is the default DBMS for Kamihi. It requires no additional setup. The database file will be created automatically in the project directory when you run your application for the first time.

You can, however, customize the location of the SQLite database file by modifying the configuration:

=== "`kamihi.yml`"
    ```yaml
    db:
      url: sqlite:///./my_database.db
    ```

=== "`.env`"
    ```bash
    KAMIHI_DB__URL=sqlite:///./my_database.db
    ```

## PostgreSQL

??? "Development PostgreSQL setup"

    The base project includes a `docker-compose.dev.yml` file that can be used to set up a PostgreSQL server for development purposes. To use it:

    1. Make sure you have Docker and Docker Compose installed on your machine.
    2. In the `docker-compose.dev.yml` file, you can find the PostgreSQL service configuration. You can modify the environment variables to set your desired username, password, and database name.
    3. Start the PostgreSQL server by running the following command in root of your project:
        <!-- termynal -->
        ```bash
        > docker-compose -f docker-compose.dev.yml up -d postgres
        [+] Running 3/3
        ✔ Network kamihi-example_default  Created                                                                                                                                                                                                                     0.1s
        ✔ Volume kamihi-example_pgdata    Created                                                                                                                                                                                                                     0.0s
        ✔ Container postgresql            Started  
        ```

To use PostgreSQL as your DBMS, you need to have a PostgreSQL server running. With that in place, you can configure your Kamihi project to connect to it by setting the database URL:

=== "`kamihi.yml`"
    ```yaml
    db:
      url: postgresql+asyncpg://username:password@localhost:5432/database_name # replace with your actual credentials
    ```
=== "`.env`"
    ```bash
    KAMIHI_DB__URL=postgresql+asyncpg://username:password@localhost:5432/database_name # replace with your actual credentials
    ```
