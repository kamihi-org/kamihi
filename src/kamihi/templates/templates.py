"""
Templates module for Kamihi.

This module provides templating functionality for the Kamihi framework, allowing
for loading and rendering templates using Jinja2. It supports loading templates
from directories or individual files and organizing them under different action
names for easy access.

The main component is the Templates class, which handles template loading,
configuration, and rendering with proper error handling for common usage patterns.

License:
MIT

Examples:
    >>> from pathlib import Path
    >>> from kamihi.templates import Templates
    >>> templates = Templates()
    >>> templates.add_directory("notifications", Path("templates/notifications"))
    >>> templates.load()
    >>> content = templates.render("notifications/welcome.md", name="User")

"""

from pathlib import Path

from jinja2 import BaseLoader, ChoiceLoader, DictLoader, Environment, FileSystemLoader, PrefixLoader, select_autoescape


class Templates:
    """
    Templates class for Kamihi.

    This class is responsible for loading and rendering templates using Jinja2.

    Attributes:
        autoreload (bool): Whether to enable auto-reloading of templates.

    """

    autoreload: bool
    _loaders: dict[str, list[BaseLoader]]
    _env: Environment | None
    _error_not_loaded: str = "Templates not loaded, call load() first."
    _error_already_loaded: str = "Cannot add templates after loading."

    def __init__(self, autoreload: bool = True) -> None:  # noqa: FBT001, FBT002
        """
        Initialize the Templates class.

        Args:
            autoreload: Whether to enable auto-reloading of templates.

        """
        self.autoreload = autoreload
        self._loaders = {}
        self._env = None

    def add_directory(self, action_name: str, path: Path) -> None:
        """
        Add a directory to the template loaders.

        This method allows you to add a directory containing templates to the
        template loaders. The templates in this directory will be loaded when
        the load() method is called.

        Args:
            action_name: The name of the action to associate with the templates.
            path: The path to the directory containing the templates.

        """
        if self._env is not None:
            raise RuntimeError(self._error_already_loaded)
        if action_name not in self._loaders:
            self._loaders[action_name] = []
        self._loaders[action_name].append(FileSystemLoader(path))

    def add_file(self, action_name: str, path: Path) -> None:
        """
        Add a file to the template loaders.

        This method allows you to add a single file to the template loaders.
        The file will be loaded when the load() method is called.
        This is useful for loading templates that are not in a directory.

        Args:
            action_name: The name of the action to associate with the template.
            path: The path to the file containing the template.

        """
        if self._env is not None:
            raise RuntimeError(self._error_already_loaded)
        if action_name not in self._loaders:
            self._loaders[action_name] = []
        self._loaders[action_name].append(DictLoader({path.name: path.read_text()}))

    def load(self) -> None:
        """
        Load the templates.

        This method initializes the Jinja2 environment and loads the templates
        from the specified loaders. It should be called after adding all the
        directories and files to the template loaders.
        """
        self._env = Environment(
            loader=PrefixLoader({name: ChoiceLoader(loaders) for name, loaders in self._loaders.items()}),
            auto_reload=self.autoreload,
            autoescape=select_autoescape(default_for_string=False),
        )

    def render(self, template_name: str, **kwargs) -> str:  # noqa: ANN003
        """
        Render a template with the given name and context.

        This method renders a template with the specified name using the
        provided keyword arguments as context. It requires that the templates
        have been loaded using the load() method before calling this method.

        Args:
            template_name: The name of the template to render.
            **kwargs: Additional keyword arguments to pass to the template.

        """
        if self._env is None:
            raise RuntimeError(self._error_not_loaded)
        template = self._env.get_template(template_name)
        return template.render(**kwargs)
