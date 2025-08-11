This guide explains how to implement a new data source type. 

Data source types are classes that inherit from the `kamihi.base.datasources.DataSource` class. They define how to connect to, and disconnect from, the data source, execute queries, and return results.

Each data source type has also an associated configuration class that inherits from `kamihi.base.datasources.DataSourceConfig`. This class defines the configuration options required for that data source type.

Data source types live in the `src/kamihi/datasources` directory. Each type, along with its configuration class, should be defined in a separate file, following the naming convention `<datasource_name>.py`.

## Implementing the data source configuration class

The data source configuration class should inherit from `kamihi.datasources.DataSourceConfig`. It should define the required configuration options for the data source type. Since the base configuration class is a `pydantic` model, you can use its features to define the configuration options.

The configuration class **MUST** include the attribute `type` with the type set to `Literal["<datasource_name>"]` and the value set to the name of the data source type. This is used by Kamihi to identify the data source type when loading the configuration.

For example, if you are implementing a new data source type called `MyDataSource`, you would create a file named `my_datasource.py` in the `src/kamihi/datasources` directory and define the configuration class like this:

```python
from kamihi.datasources import DataSourceConfig
from typing import Literal

class MyDataSourceConfig(DataSourceConfig):
    """
    Configuration model for MyDataSource.
    
    Attributes:
        option1 (str): Description of option1.
        option2 (int): Description of option2. Default is 42.
    """
    type: Literal["my_datasource"] = "my_datasource"

    option1: str
    option2: int = 42  # Default value
```

!!! info
    Be sure to correctly document all the configuration options in the class docstring, as this will be used to generate the documentation for the data source type.

## Implementing the data source type class

The data source type class should inherit from `kamihi.datasources.DataSource`. It should implement the following methods:

- `async def connect(self): ...`: Establishes a connection to the data source.
- `async def fetch(self, query: str | Path) -> list[dict]: ...`: Executes a query and returns the results as a list of dictionaries.
- `async def disconnect(self): ...`: Closes the connection to the data source.

The class has access to the configuration options defined in the configuration class through the `self.config` attribute, which is an instance of the configuration class defined earlier.

For example, continuing with the `MyDataSource` example, you would implement the data source type class like this:

```python
from kamihi.datasources import DataSource
from pathlib import Path

class MyDataSource(DataSource):
    async def connect(self):
        # Implement the logic to establish a connection to the data source
        self.connection = "Connected to MyDataSource"  # Placeholder for actual connection logic
        print(self.connection)

    async def fetch(self, query: str | Path) -> list[dict]:
        # Implement the logic to execute the query and return results
        print(f"Executing query: {query}")
        return [{"result": "data from MyDataSource"}]  # Placeholder for actual query results

    async def disconnect(self):
        # Implement the logic to close the connection to the data source
        print("Disconnecting from MyDataSource")
        self.connection = None
```

The `kamihi.base.utils` package provides utility functions to help with common tasks, such as timing requests and handling exceptions. You can use these utilities in your data source type implementation as needed. Consult one of the existing data source types for examples of how to use these utilities.

## Handling dependencies

Each datasource type has its own set of dependencies, and these are normally heavy and not needed for all Kamihi applications. To avoid unnecessary dependencies in user installations, you should define any dependencies in a separate dependency group in the `pyproject.toml` file or when using `uv` to add them to the framework.

For example, if your data source type requires the `requests` library:

=== "pyproject.toml"

    ```toml
    [project.optional-dependencies]
    my_datasource = [
        "requests>=2.25.1"
    ]
    all = [
        "requests>=2.25.1",  # Include in the 'all' group
        # other dependencies...
    ]
    ```

=== "Using `uv`'s CLI"

    ```bash
    uv add --optional my_datasource --optional all requests>=2.25.1
    ```

!!! info
    Remember to also add the dependency to the `all` optional dependencies group.

Since the dependencies are optional, users may try to use the data source type without having the required dependencies installed.

To avoid this, you should decorate every method that requires the dependencies with the `@requires("<optional_group_name>")` decorator from `kamihi.base.utils` and import the required dependencies **inside** the method. This decorator will raise an exception if the required dependencies are not installed, providing a clear error message to the user.

```python
from kamihi.base.utils import requires

class MyDataSource(DataSource):
    @requires("my_datasource")
    async def connect(self):
        import requests  # Importing inside the method will ensure the dependency is available
        # Implement the logic to establish a connection to the data source
        self.connection = "Connected to MyDataSource"  # Placeholder for actual connection logic
        print(self.connection)
```

## Registering the data source type

Once you have implemented the data source type and its configuration class, you need to register it with Kamihi. This is done by adding the data source type to the `kamihi.datasources` module's `__all__` list.

```python
from kamihi.datasources.my_datasource import MyDataSource, MyDataSourceConfig

__all__ = [
    ..., # other existing data sources
    "MyDataSource", 
    "MyDataSourceConfig"
]
```

## Testing your data source type

To ensure your data source type works correctly, you should write unit and functional tests for it. Refer to the [Testing guide](../testing.md) for more information on how to write tests for Kamihi.

## Checklist

- [ ] Define any dependencies **as optional** in the `pyproject.toml` or using `uv`.
- [ ] Implement the data source configuration class.
- [ ] Implement the data source type class.
- [ ] Register the data source type in `kamihi.datasources`.
- [ ] Write unit and functional tests for your data source type.
- [ ] Add your datasource config type to the table in the [Configure datasources guide](../../guides/config/configure-datasources.md).
- [ ] Create a pull request with your changes.
