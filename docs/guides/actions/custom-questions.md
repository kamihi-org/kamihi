This guide explains how to create custom reusable questions in Kamihi, allowing you to encapsulate complex validation and logic that can be reused across multiple actions.

## Creating custom reusable questions

Sometimes, the same question is used in multiple actions, and might have complex validation or other logic. In these cases, it is recommended to create a custom question class that can be reused across actions.

Custom questions live in the `questions` folder in the root of your Kamihi project.

To create a custom question, create a new Python file in the `questions` folder in the root of your Kamihi project and define a class that inherits from one of the base question types. For example:

```python
from kamihi.questions import String

class EmailQuestion(String):
    def __init__(self, prompt: str):
        super().__init__(
            prompt,
            pattern=r"^[\w\.-]+@[\w\.-]+\.\w+$",
            error_text="Please enter a valid email address."
        )
```

This custom question `EmailQuestion` inherits from `String` and adds a regex pattern to validate that the input is a valid email address.

You can then use this custom question in your actions by importing it:

```python
from kamihi import bot
from typing import Annotated

from questions.email_question import EmailQuestion

@bot.action
async def register_user(
        email: Annotated[
            str,
            EmailQuestion("What is your email address?")
        ]
) -> str:
    return f"Registered email: {email}"
```

??? tip "Cleaner imports"
    Right now, if you want to use both standard and custom questions in your actions, you will need to import them separately.
    
    ```python
    from kamihi.questions import String, Integer
    from questions.email_question import EmailQuestion
    ```
    
    To keep your imports cleaner, you can create an `__init__.py` file in the `questions` folder that re-exports your custom questions along with the standard ones. For example:
    
    ```python
    from kamihi.questions import *
    from .email_question import EmailQuestion
    ```
    
    This way, you can import all questions from the `questions` folder with a single import statement:
        ```python
    from questions import EmailQuestion, String, Integer
    ```

## Complex validation

For more complex validation logic that cannot be easily handled with regex patterns or simple checks, there are several methods you can override in your custom question classes:

- `validate_before(self, response: Any) -> Any`: This method is called before any built-in validation and type casting. You can use it to implement custom pre-validation logic.
- `validate_after(self, response: Any) -> Any`: This method is called after built-in validation and type casting. You can use it to implement custom post-validation logic.
- `_validate_internal(self, response: Any) -> Any`: This method is where the built-in validation logic is implemented. Only override this method when you are creating a completely custom question that inherits directly from the `Question` base type.
- `validate(self, response: Any) -> Any`: This is the main validation method that is called when validating a response. It calls `validate_before`, the built-in validation logic, and `validate_after` in sequence. You can override this method to customize the entire validation process.

On all validators, you can raise a `ValueError` with a custom error message to indicate that the validation has failed. The error message specified for the `ValueError` will be sent to the user, and they can try to answer the question again.

For example, here is a custom question that asks for a color but does not allow the color "red":

```python
from kamihi.questions import String

class NoRedColorQuestion(String):
    def validate_after(self, response: str) -> str:
        if response.lower() == "red":
            raise ValueError("The color red is not allowed.")
        return response
```

Another example: a date choice that does not allow weekends:

```python
from kamihi.questions import Date
import datetime

class WeekdayDateQuestion(Date):
    def validate_after(self, response: datetime.date) -> datetime.date:
        if response.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            raise ValueError("Please choose a weekday (Monday to Friday).")
        return response
```

Another example: a string question that asks for the user's full name, makes it title case before validation, and ensures that it contains at least two words:

```python
from kamihi.questions import String

class FullNameQuestion(String):
    def validate_before(self, response: str) -> str:
        # Convert to title case before validation
        return response.title()

    def validate_after(self, response: str) -> str:
        # Ensure the name contains at least two words
        if len(response.split()) < 2:
            raise ValueError("Please enter your full name (at least first and last name).")
        return response
```

Yet another example: a dynamic choice question that always uses the same request (so you avoid specifying it every time):

```python
from kamihi.questions import DynamicChoice

class CountryChoiceQuestion(DynamicChoice):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            **kwargs,
            request="countries.geographic_db.sql"  # Path to the request file inside the `questions` folder
        )
```

## Further customizing custom questions

In addition to validation, you can further customize your custom question classes by overriding other methods and properties from the base question types. Some useful methods and properties you might want to override include:

- `ask_question(self, update: Update, context: Context) -> None`: This method is responsible for sending the question prompt to the user. You can override it to customize how the question is presented.
- `filters(self) -> filters.BaseFilter` (property): This property returns a list of filters from `python-telegram-bot` that are applied to the user's response. You can override it to add custom filters for the responses, so that only valid responses are processed, while the rest are ignored.
- `get_response(self, update: Update, context: Context) -> Any`: This method extracts the user's response from the update object. You can override it to customize how the response is retrieved.

To consult the full list of methods and properties available for customization, refer to the [API reference for the `Question` base class](../../reference/kamihi/questions/question.md#kamihi.questions.question.Question').
