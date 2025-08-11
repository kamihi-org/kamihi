"""
Base class for data sources in Kamihi.

License:
    MIT
"""

from pathlib import Path
from types import NoneType
from typing import Annotated, Any, ClassVar, Union

from pydantic import BaseModel, Field


class DataSourceConfig(BaseModel):
    """
    Configuration model for data sources.

    This model defines the configuration schema for data sources in Kamihi.
    It includes the name of the data source and any additional parameters required
    for its initialization.

    Attributes:
        name (str): The name of the data source. Must be unique across all data sources.

    """

    name: str
    _registry: ClassVar[dict[str, type["DataSourceConfig"]]] = {}

    @classmethod
    def _build_registry(cls) -> None:
        """Build the registry of data source configuration classes."""
        for subclass in cls.__subclasses__():
            type_name = subclass.model_fields.get("type").default
            if type_name:
                cls._registry[type_name] = subclass

    @classmethod
    def union_type(cls) -> type[Annotated] | NoneType:
        """
        Get a union type of all registered data source configuration classes.

        Returns:
            Union[type[DataSourceConfig], ...]: A union type of all registered data source configuration classes.

        """
        if not cls._registry.values():
            cls._build_registry()
        return (
            Annotated[
                Union[tuple(cls._registry.values())],  # noqa: UP007
                Field(discriminator="type"),
            ]
            if cls._registry
            else NoneType
        )


class DataSource:
    """
    Base class for data sources in Kamihi.

    This class serves as a template for creating specific data source implementations.
    It defines the basic structure and methods that all data sources should implement.
    """

    _registry: dict[str, type["DataSource"]] = {}

    @classmethod
    def _build_registry(cls) -> None:
        """Build the registry of data source classes."""
        for subclass in cls.__subclasses__():
            type_name = getattr(subclass, "type", None)
            if type_name:
                cls._registry[type_name] = subclass

    @classmethod
    def get_datasource_class(cls, type_name: str) -> type["DataSource"] | None:
        """
        Get the data source class by its type name.

        Args:
            type_name (str): The type name of the data source.

        Returns:
            type[DataSource] | None: The data source class if found, otherwise None.

        """
        if not cls._registry:
            cls._build_registry()
        return cls._registry.get(type_name)

    def __init__(self, settings: DataSourceConfig) -> None:
        """
        Initialize the DataSource with a name.

        Args:
            settings (str): The name of the data source.

        """
        self.settings = settings

    async def connect(self) -> None:  # noqa: ANN002, ANN003, ARG002
        """
        Connect to the data source.

        This method can be implemented, if needed, to establish a connection
        to the data source. By default, it does nothing.

        """
        raise NotImplementedError("Subclasses must implement this method.")

    async def fetch(self, request: Path | str) -> Any:  # noqa: ANN002, ANN003, ANN401
        """
        Asynchronously fetch data from the data source.

        This method should be implemented by subclasses to define how data is retrieved
        from the specific data source in an asynchronous manner.

        Args:
            request (Path | str): The request to fetch data from the data source.
                This could be a file path, URL, or any identifier for the data.

        Returns:
            The fetched data.

        """
        raise NotImplementedError("Subclasses must implement this method.")

    async def disconnect(self) -> None:
        """
        Disconnect from the data source.

        This method can be implemented, if needed, to close the connection
        to the data source. By default, it does nothing.

        """
        raise NotImplementedError("Subclasses must implement this method.")
