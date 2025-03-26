"""
TODO: one-line module description.

TODO: Additional details about the module, its purpose, and any necessary
background information. Explain what functions or classes are included.

License:
    MIT

Examples:
    [Examples of how to use the module/classes/functions]

Attributes:
    [List any relevant module-level attributes with types and descriptions]

"""

from kamihi import hello


def test_hello_returns_greeting_with_name():
    result = hello("Alice")
    assert result == "Hello from Kamihi, Alice!"


def test_hello_with_empty_name():
    result = hello("")
    assert result == "Hello from Kamihi, !"


def test_hello_with_special_characters():
    result = hello("@#$%^")
    assert result == "Hello from Kamihi, @#$%^!"


def test_hello_with_numeric_input():
    result = hello("123")
    assert result == "Hello from Kamihi, 123!"


def test_hello_with_multiline_name():
    result = hello("John\nDoe")
    assert result == "Hello from Kamihi, John\nDoe!"
