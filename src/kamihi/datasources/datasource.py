"""
Base class for data sources in Kamihi.

License:
    MIT
"""

from typing import Any

from pydantic import BaseModel


class DataSourceConfig(BaseModel):
    """
    Configuration model for data sources.

    This model defines the configuration schema for data sources in Kamihi.
    It includes the name of the data source and any additional parameters required
    for its initialization.

    Attributes:
        name (str): The name of the data source.

    """

    name: str


class DataSource:
    """
    Base class for data sources in Kamihi.

    This class serves as a template for creating specific data source implementations.
    It defines the basic structure and methods that all data sources should implement.
    """

    def __init__(self, settings: DataSourceConfig) -> None:
        """
        Initialize the DataSource with a name.

        Args:
            settings (str): The name of the data source.

        """
        self.settings = settings

    def fetch(self, *args, **kwargs) -> Any:  # noqa: ANN002, ANN003, ANN401
        """
        Fetch data from the data source.

        This method should be implemented by subclasses to define how data is retrieved
        from the specific data source.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The fetched data.

        """
        raise NotImplementedError("Subclasses must implement this method.")

    async def afetch(self, *args, **kwargs) -> Any:  # noqa: ANN002, ANN003, ANN401
        """
        Asynchronously fetch data from the data source.

        This method should be implemented by subclasses to define how data is retrieved
        from the specific data source in an asynchronous manner.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            The fetched data.

        """
        raise NotImplementedError("Subclasses must implement this method.")
