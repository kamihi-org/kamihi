This guide describes how to use templates in Kamihi actions to create dynamic messages and content. Templates allow you to define a structure for your messages while dynamically inserting values at runtime.

## Writing templates

Templates in Kamihi are created using Jinja2 syntax. You can create a template by defining a string with placeholders that will be replaced with actual values when the action is executed. For example:

```md
Hello, {{ user.name }}! Welcome to our service.
```

You can also use more complex expressions and control structures, such as loops and conditionals, to create dynamic content. For example:

```md
{% if user.is_premium %}
Thank you for being a premium member, {{ user.name }}!
{% else %}
Thank you for using our service, {{ user.name }}! Consider upgrading to premium for more features.
{% endif %}
```

!!! info
    For more information on Jinja2 syntax, refer to the [Jinja2 documentation](https://jinja.palletsprojects.com/en/3.0.x/templates/).

## Storing templates

Templates are stored in the folder of the action that uses them. **The template file must have a `.md.jinja` extension**, indicating that it is a Markdown template processed by Jinja2.

By default, Kamihi will look for a template file with the same name as the action in the action's folder. For example, if your action is `start`, Kamihi will look for a file named `start.md.jinja` in the `actions/start/` directory.

## Using templates in actions

To use templates in Kamihi actions, you request the `template` parameter in the action's parameters. For example:

=== "actions/start/start.py"

    ```python
    from kamihi import bot
    from jinja2 import Template
    
    @bot.action
    async def start(template: Template):
        return template.render(name="John Doe")
    ```

=== "actions/start/start.md.jinja"

    ```md
    Hello, {{ name }}! Welcome to our service.
    ```

## Templates with custom names

If you want to use a template with a custom name, you can specify the template file in the action's parameters using the Annotated syntax. For example:

=== "actions/start/start.py"

    ```python
    from kamihi import bot
    from jinja2 import Template
    from typing import Annotated
    
    @bot.action
    async def custom_action(template: Annotated[Template, "custom_template_name.md.jinja"]):
        return template.render(name="John Doe")
    ```

=== "actions/start/custom_template_name.md.jinja"

    ```md
    Hello, {{ name }}! This is a custom template.
    ```

Kamihi will look recursively for the template file in the same directory as the action, meaning that you can organize your templates in subdirectories if needed, but in the Annotation you should only specify the file name, not the path. 

For example, if you have a template in `actions/start/templates/custom_template_name.md.jinja`, you use it with the annotation `Annotated[Template, "custom_template_name.md.jinja"]`.

## Using multiple templates

You can also use multiple templates in a single action. To do this, you can define multiple template parameters in the action's signature, as long as they all start with the `template` prefix. For example:

=== "actions/start/start.py"

    ```python
    from kamihi import bot
    from jinja2 import Template
    from typing import Annotated
    
    @bot.action
    async def multi_template_action(
        template_main: Annotated[Template, "main_template.md.jinja"],
        template_secondary: Annotated[Template, "secondary_template.md.jinja"]
    ):
        main_content = template_main.render(name="John Doe")
        secondary_content = template_secondary.render(name="John Doe")
        return f"{main_content}\n\n{secondary_content}"
    ```

=== "actions/start/main_template.md.jinja"

    ```md
    Hello, {{ name }}! This is the main template.
    ```

=== "actions/start/secondary_template.md.jinja"

    ```md
    Hello, {{ name }}! This is the secondary template.
    ```

You can also mix and match between the default template and custom templates. For example, you can use the default template for the main content and a custom template for the secondary content:

```python
from kamihi import bot
from jinja2 import Template
from typing import Annotated

@bot.action
async def mixed_template(
    template: Template,  # Default template at `mixed_template.md.jinja`
    template_secondary: Annotated[Template, "secondary_template.md.jinja"]
):
    main_content = template.render(name="John Doe")
    secondary_content = template_secondary.render(name="John Doe")
    return f"{main_content}\n\n{secondary_content}"
```

## The `templates` parameter

You can also request the `templates` parameter in your action to access all templates in the action's folder. This is useful if you want to use multiple templates without specifying each one individually. The `templates` parameter will be a dictionary where the keys are the template names and the values are the rendered templates.

```python
from kamihi import bot
from jinja2 import Template

@bot.action
async def start(templates: dict[str, Template]):
    main_content = templates["start.md.jinja"].render(name="John Doe")
    secondary_content = templates["secondary_template.md.jinja"].render(name="John Doe")
    return f"{main_content}\n\n{secondary_content}"
```
