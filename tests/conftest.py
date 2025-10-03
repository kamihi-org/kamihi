"""
Common fixtures and utilities for testing.

License:
    MIT

"""

pytest_plugins = [
    "tests.fixtures.app",
    "tests.fixtures.docker_container",
    "tests.fixtures.docker_files",
    "tests.fixtures.hooks",
    "tests.fixtures.settings",
    "tests.fixtures.tg",
]
