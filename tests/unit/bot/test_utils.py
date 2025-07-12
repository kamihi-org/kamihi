"""
Tests for the kamihi.bot.utils module.

License:
    MIT
"""

from typing import Annotated
from kamihi.bot.utils import parse_annotation


def test_parse_annotation_with_basic_type():
    """Test parsing a basic type annotation without metadata."""
    result = parse_annotation(int)
    assert result == (int, None)


def test_parse_annotation_with_annotated_type():
    """Test parsing an Annotated type with metadata."""
    ann = Annotated[int, "meta"]
    result = parse_annotation(ann)
    assert result == (int, "meta")


def test_parse_annotation_with_annotated_type_complex_metadata():
    """Test parsing an Annotated type with complex metadata."""
    ann = Annotated[str, {"key": "value"}]
    result = parse_annotation(ann)
    assert result == (str, {"key": "value"})


def test_parse_annotation_with_non_annotated_type():
    """Test parsing a non-annotated type."""

    class Dummy:
        pass

    result = parse_annotation(Dummy)
    assert result == (Dummy, None)
