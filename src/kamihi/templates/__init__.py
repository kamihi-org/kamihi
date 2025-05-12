"""
Template module for Kamihi.

This module provides the Templates class, which is responsible for loading
and rendering templates using Jinja2. The class allows for the addition of
directories and files to the template loaders, enabling dynamic loading of
templates at runtime.

License:
    MIT

Examples:
    >>> from kamihi.templates import Templates
    >>> from pathlib import Path
    >>> tmps = Templates()
    >>> tmps.add_directory("example_action", Path("/path/to/templates"))
    >>> tmps.load()
    >>> rendered_template = tmps.render("example_action/template_name.md", context={"key": "value"})

"""

from .templates import Templates

__all__ = ["Templates"]
