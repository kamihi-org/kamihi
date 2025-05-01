"""
Tests for the Templates module in Kamihi.

This module contains tests for the Templates class, which provides templating
functionality for the Kamihi framework. The tests verify template loading,
rendering, error handling, and other features of the Templates class.

License:
    MIT

"""

import tempfile
from pathlib import Path

import pytest
from jinja2 import TemplateNotFound, TemplateSyntaxError

from kamihi.templates.templates import Templates


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for test templates."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield Path(tmpdirname)


@pytest.fixture
def simple_template(temp_dir):
    """Create a simple template file."""
    template_path = temp_dir / "simple.txt"
    template_path.write_text("Hello World!")
    return template_path


@pytest.fixture
def variable_template(temp_dir):
    """Create a template with variables."""
    template_path = temp_dir / "variable.txt"
    template_path.write_text("Hello {{ name }}!")
    return template_path


@pytest.fixture
def complex_template(temp_dir):
    """Create a template with complex Jinja2 features."""
    template_path = temp_dir / "complex.txt"
    content = """
    {% if show_greeting %}
    Hello {{ name }}!
    {% endif %}
    
    {% for item in items %}
    - {{ item }}
    {% endfor %}
    
    {% if user %}
    User: {{ user.name }}, Age: {{ user.age }}
    {% endif %}
    """
    template_path.write_text(content)
    return template_path


@pytest.fixture
def template_directory(temp_dir):
    """Create a directory with multiple templates."""
    template_dir = temp_dir / "templates"
    template_dir.mkdir()

    # Create multiple templates in the directory
    (template_dir / "welcome.txt").write_text("Welcome to {{ service }}!")
    (template_dir / "goodbye.txt").write_text("Goodbye from {{ service }}!")

    return template_dir


def test_init_default_autoreload():
    """Test initialization with default autoreload parameter."""
    templates = Templates()
    assert templates.autoreload is True
    assert templates._env is None
    assert templates._loaders == {}


@pytest.mark.parametrize("autoreload", [True, False])
def test_init_explicit_autoreload(autoreload):
    """Test initialization with explicit autoreload values."""
    templates = Templates(autoreload=autoreload)
    assert templates.autoreload is autoreload


def test_add_directory_with_valid_path(template_directory):
    """Test adding a directory with a valid path."""
    templates = Templates()
    templates.add_directory("emails", template_directory)

    assert "emails" in templates._loaders
    assert len(templates._loaders["emails"]) == 1


def test_add_directory_with_nonexistent_path():
    """Test adding a directory with a non-existent path."""
    templates = Templates()
    # This shouldn't raise an exception, as FileSystemLoader doesn't validate immediately
    templates.add_directory("emails", Path("/nonexistent/path"))

    assert "emails" in templates._loaders


def test_add_file_with_valid_file(simple_template):
    """Test adding a file with a valid path."""
    templates = Templates()
    templates.add_file("notices", simple_template)

    assert "notices" in templates._loaders
    assert len(templates._loaders["notices"]) == 1


def test_add_file_with_nonexistent_file():
    """Test adding a file with a non-existent path."""
    templates = Templates()
    with pytest.raises(FileNotFoundError):
        templates.add_file("notices", Path("/nonexistent/file.txt"))


def test_add_multiple_templates_to_same_action(simple_template, variable_template):
    """Test adding multiple templates to the same action name."""
    templates = Templates()
    templates.add_file("notices", simple_template)
    templates.add_file("notices", variable_template)

    assert "notices" in templates._loaders
    assert len(templates._loaders["notices"]) == 2


def test_add_templates_to_different_actions(simple_template, variable_template):
    """Test adding templates to different action names."""
    templates = Templates()
    templates.add_file("notices", simple_template)
    templates.add_file("emails", variable_template)

    assert "notices" in templates._loaders
    assert "emails" in templates._loaders
    assert len(templates._loaders["notices"]) == 1
    assert len(templates._loaders["emails"]) == 1


def test_load_with_empty_loaders():
    """Test loading with no templates added."""
    templates = Templates()
    templates.load()

    assert templates._env is not None


def test_load_with_multiple_sources(template_directory, simple_template):
    """Test loading with multiple template sources."""
    templates = Templates()
    templates.add_directory("emails", template_directory)
    templates.add_file("notices", simple_template)
    templates.load()

    assert templates._env is not None
    # Verify loader names in the PrefixLoader
    assert sorted(templates._env.loader.mapping.keys()) == ["emails", "notices"]


def test_load_sets_up_environment_correctly():
    """Test that loading sets up the Jinja2 environment correctly."""
    templates = Templates(autoreload=False)
    templates.load()

    assert templates._env is not None
    assert templates._env.auto_reload is False
    assert templates._env.autoescape is not None


def test_render_simple_template(simple_template):
    """Test rendering a simple template without variables."""
    templates = Templates()
    templates.add_file("notices", simple_template)
    templates.load()

    result = templates.render("notices/simple.txt")
    assert result == "Hello World!"


def test_render_template_with_variables(variable_template):
    """Test rendering a template with variables."""
    templates = Templates()
    templates.add_file("emails", variable_template)
    templates.load()

    result = templates.render("emails/variable.txt", name="User")
    assert result == "Hello User!"


def test_render_from_different_namespaces(template_directory):
    """Test rendering templates from different action namespaces."""
    templates = Templates()
    templates.add_directory("emails", template_directory)
    templates.load()

    welcome = templates.render("emails/welcome.txt", service="Kamihi")
    goodbye = templates.render("emails/goodbye.txt", service="Kamihi")

    assert welcome == "Welcome to Kamihi!"
    assert goodbye == "Goodbye from Kamihi!"


def test_render_with_complex_context(complex_template):
    """Test rendering with complex context data."""
    templates = Templates()
    templates.add_file("reports", complex_template)
    templates.load()

    context = {
        "show_greeting": True,
        "name": "Admin",
        "items": ["Item 1", "Item 2", "Item 3"],
        "user": {"name": "John", "age": 30},
    }

    result = templates.render("reports/complex.txt", **context)
    assert "Hello Admin!" in result
    assert "- Item 1" in result
    assert "- Item 2" in result
    assert "- Item 3" in result
    assert "User: John, Age: 30" in result


def test_identical_template_in_multiple_namespaces(temp_dir):
    """Test adding identical template content to multiple namespaces."""
    templates = Templates()

    # Create identical templates in different directories
    dir1 = temp_dir / "dir1"
    dir1.mkdir()
    template1 = dir1 / "greeting.txt"
    template1.write_text("Hello {{ name }}!")

    dir2 = temp_dir / "dir2"
    dir2.mkdir()
    template2 = dir2 / "greeting.txt"
    template2.write_text("Hello {{ name }}!")

    templates.add_directory("action1", dir1)
    templates.add_directory("action2", dir2)
    templates.load()

    result1 = templates.render("action1/greeting.txt", name="User1")
    result2 = templates.render("action2/greeting.txt", name="User2")

    assert result1 == "Hello User1!"
    assert result2 == "Hello User2!"


def test_template_formatting_consistency(temp_dir):
    """Test that templates maintain consistent formatting when used across actions."""
    template_content = """
    Title: {{ title }}
    
    Content:
      - {{ item1 }}
      - {{ item2 }}
    
    Regards,
    {{ sender }}
    """

    # Create templates in different directories with same format
    dir1 = temp_dir / "dir1"
    dir1.mkdir()
    (dir1 / "format.txt").write_text(template_content)

    dir2 = temp_dir / "dir2"
    dir2.mkdir()
    (dir2 / "format.txt").write_text(template_content)

    templates = Templates()
    templates.add_directory("action1", dir1)
    templates.add_directory("action2", dir2)
    templates.load()

    context1 = {"title": "First", "item1": "A", "item2": "B", "sender": "Team1"}
    context2 = {"title": "Second", "item1": "C", "item2": "D", "sender": "Team2"}

    result1 = templates.render("action1/format.txt", **context1)
    result2 = templates.render("action2/format.txt", **context2)

    # Check structure is preserved while content differs
    assert "Title: First" in result1
    assert "Title: Second" in result2
    assert "- A" in result1
    assert "- C" in result2
    assert "Regards,\n    Team1" in result1
    assert "Regards,\n    Team2" in result2


def test_template_inheritance(temp_dir):
    """Test template inheritance across different action namespaces."""
    # Create base template
    base_dir = temp_dir / "base"
    base_dir.mkdir()
    base_template = base_dir / "base.html"
    base_template.write_text("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{% block title %}Default Title{% endblock %}</title>
    </head>
    <body>
        {% block content %}
        Default content
        {% endblock %}
    </body>
    </html>
    """)

    # Create template that extends the base
    child_dir = temp_dir / "child"
    child_dir.mkdir()
    child_template = child_dir / "child.html"
    child_template.write_text("""
    {% extends "base/base.html" %}
    {% block title %}{{ custom_title }}{% endblock %}
    {% block content %}
    <h1>{{ heading }}</h1>
    <p>{{ paragraph }}</p>
    {% endblock %}
    """)

    templates = Templates()
    templates.add_directory("base", base_dir)
    templates.add_directory("child", child_dir)
    templates.load()

    result = templates.render(
        "child/child.html", custom_title="Custom Page", heading="Welcome", paragraph="This is a custom page."
    )

    assert "<title>Custom Page</title>" in result
    assert "<h1>Welcome</h1>" in result
    assert "<p>This is a custom page.</p>" in result


def test_update_context_variables(variable_template):
    """Test updating context variables and verifying changes in output."""
    templates = Templates()
    templates.add_file("greetings", variable_template)
    templates.load()

    result1 = templates.render("greetings/variable.txt", name="Alice")
    result2 = templates.render("greetings/variable.txt", name="Bob")

    assert result1 == "Hello Alice!"
    assert result2 == "Hello Bob!"


def test_variable_values_in_multiple_instances(variable_template):
    """Test that variable values are correctly reflected in all instances."""
    templates = Templates()
    templates.add_file("greetings1", variable_template)
    templates.add_file("greetings2", variable_template)
    templates.load()

    # Same template, different namespaces, different variables
    result1 = templates.render("greetings1/variable.txt", name="Team1")
    result2 = templates.render("greetings2/variable.txt", name="Team2")

    assert result1 == "Hello Team1!"
    assert result2 == "Hello Team2!"


def test_conditional_syntax(temp_dir):
    """Test templates with conditional syntax."""
    template_path = temp_dir / "conditional.txt"
    template_path.write_text("""
    {% if show_greeting %}
    Hello {{ name }}!
    {% else %}
    No greeting for you.
    {% endif %}
    """)

    templates = Templates()
    templates.add_file("tests", template_path)
    templates.load()

    result1 = templates.render("tests/conditional.txt", show_greeting=True, name="User")
    result2 = templates.render("tests/conditional.txt", show_greeting=False, name="User")

    assert "Hello User!" in result1
    assert "No greeting for you." in result2


def test_loop_syntax(temp_dir):
    """Test templates with loop syntax."""
    template_path = temp_dir / "loop.txt"
    template_path.write_text("""
    Items:
    {% for item in items %}
    - {{ item }} ({{ loop.index }}/{{ loop.length }})
    {% endfor %}
    """)

    templates = Templates()
    templates.add_file("tests", template_path)
    templates.load()

    result = templates.render("tests/loop.txt", items=["Apple", "Banana", "Cherry"])

    assert "- Apple (1/3)" in result
    assert "- Banana (2/3)" in result
    assert "- Cherry (3/3)" in result


def test_filters(temp_dir):
    """Test templates with Jinja2 filters."""
    template_path = temp_dir / "filters.txt"
    template_path.write_text("""
    {{ name | upper }}
    {{ text | truncate(10) }}
    {{ list | join(', ') }}
    """)

    templates = Templates()
    templates.add_file("tests", template_path)
    templates.load()

    result = templates.render(
        "tests/filters.txt", name="john", text="This is a long text that should be truncated", list=["a", "b", "c"]
    )

    assert "JOHN" in result
    assert "This..." in result
    assert "a, b, c" in result


def test_macros_and_includes(temp_dir):
    """Test templates with macros and includes."""
    # Create macro file
    macro_dir = temp_dir / "macros"
    macro_dir.mkdir()
    macro_file = macro_dir / "utils.txt"
    macro_file.write_text("""
    {% macro render_item(item) %}
    <div>{{ item.name }}: {{ item.value }}</div>
    {% endmacro %}
    """)

    # Create template that uses the macro
    template_file = temp_dir / "using_macro.txt"
    template_file.write_text("""
    {% import "macros/utils.txt" as utils %}
    
    {{ utils.render_item(item1) }}
    {{ utils.render_item(item2) }}
    """)

    templates = Templates()
    templates.add_directory("macros", macro_dir)
    templates.add_file("templates", template_file)
    templates.load()

    result = templates.render(
        "templates/using_macro.txt", item1={"name": "First", "value": 100}, item2={"name": "Second", "value": 200}
    )

    assert "<div>First: 100</div>" in result
    assert "<div>Second: 200</div>" in result


def test_escaping_special_characters(temp_dir):
    """Test escaping special characters in templates."""
    template_path = temp_dir / "escape.txt"
    template_path.write_text("{{ content }}")

    templates = Templates()
    templates.add_file("tests", template_path)
    templates.load()

    html_content = "<script>alert('XSS')</script>"
    result = templates.render("tests/escape.txt", content=html_content)

    # Since autoescape=False by default, content should not be escaped
    assert result == html_content


def test_add_after_loading(temp_dir):
    """Test adding templates after loading (should raise RuntimeError)."""
    templates = Templates()
    templates.load()

    with pytest.raises(RuntimeError) as excinfo:
        templates.add_directory("action", temp_dir)

    assert "Cannot add templates after loading" in str(excinfo.value)

    with pytest.raises(RuntimeError) as excinfo:
        templates.add_file("action", temp_dir / "file.txt")

    assert "Cannot add templates after loading" in str(excinfo.value)


def test_render_before_loading(temp_dir):
    """Test rendering before loading (should raise RuntimeError)."""
    templates = Templates()

    with pytest.raises(RuntimeError) as excinfo:
        templates.render("any/template.txt")

    assert "Templates not loaded, call load() first" in str(excinfo.value)


def test_render_nonexistent_template():
    """Test rendering a non-existent template."""
    templates = Templates()
    templates.load()

    with pytest.raises(TemplateNotFound) as _:
        templates.render("nonexistent/template.txt")


def test_syntactically_invalid_template(temp_dir):
    """Test with syntactically invalid templates."""
    template_path = temp_dir / "invalid.txt"
    template_path.write_text("{% if unclosed condition %}")  # Missing endif

    templates = Templates()
    templates.add_file("tests", template_path)
    templates.load()

    with pytest.raises(TemplateSyntaxError) as _:
        templates.render("tests/invalid.txt")


def test_empty_template_files(temp_dir):
    """Test with empty template files."""
    empty_file = temp_dir / "empty.txt"
    empty_file.write_text("")

    templates = Templates()
    templates.add_file("tests", empty_file)
    templates.load()

    result = templates.render("tests/empty.txt")
    assert result == ""


def test_unicode_characters(temp_dir):
    """Test with Unicode/special characters in templates."""
    unicode_file = temp_dir / "unicode.txt"
    unicode_file.write_text("Unicode: {{ text }} 日本語 Español")

    templates = Templates()
    templates.add_file("tests", unicode_file)
    templates.load()

    result = templates.render("tests/unicode.txt", text="こんにちは")
    assert "Unicode: こんにちは 日本語 Español" in result
