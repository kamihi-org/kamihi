In this tutorial, you will learn how to work with users, roles and permissions, as well as how to extend the user model in Kamihi to store custom user-specific data.

By the end of this tutorial, you will have a basic permission system in place, and an action that allows users to select and save their favorite store from a list retrieved from a datasource.

## Users, roles, and permissions

First, let's briefly review the basic concepts of users, roles, and permissions in Kamihi.

- **Users**: Represent individuals interacting with your bot. Each user has a unique identifier given by Telegram.
- **Roles**: Define groups of users. A user can belong to multiple roles, and roles can have many users.
- **Permissions**: Specify which actions a user and/or role can execute.

If you take a look at the admin web interface, you will see a section for each of these. You can create users, assign them roles, and define permissions for those roles from there. You can also use the CLI to manage users, roles, and permissions if you prefer.

## Extending the user model

Kamihi allows you to extend the default user model with custom fields. This is very useful for storing user-specific data that is not part of the default model.

Models in Kamihi are defined using SQLAlchemy, so you can add new fields to the user model just like you would with any other SQLAlchemy model.

For example, let's say we want to store the user's favorite store. We can extend the user model like this:

=== "models/user.py"

    ```python
    from kamihi.db import BaseUser
    from sqlalchemy import Integer
    from sqlalchemy.orm import Mapped, mapped_column
    
    class User(BaseUser):
        __table_args__ = {'extend_existing': True}  # (1)!
        favorite_store_id: Mapped[int] = mapped_column(Integer, nullable=True)  # (2)!

    ```

    1. If you modify or delete this line, everything will explode, so try not to.
    2. We add a new field `favorite_store_id` to store the user's favorite store. This field is nullable, as not all users will have a favorite store.

!!! warning "Database migration"
    After modifying the user model, you need to create and apply a database migration to update the database schema. Just as a reminder, the commands are `kamihi db migrate` and `kamihi db upgrade`.
    Make sure to run these commands in your terminal after saving the changes to the user model, otherwise there could be errors and even data loss.

## Store question

We want to ask the user to select their favorite store. This means we need another question, and since this also sounds like a common use case, we will also create a new question type for it.

We will need to create a query file to retrieve the list of stores from the Sakila datasource, and then create a new question that uses this query to present the list of stores to the user. 

The query, however, has more complexity than previous ones we have seen, because:

- The list of stores only has reference fields: to its address, to its manager, etc. and the data for them is stored in other tables.
- We need to save the store's ID but the user will not be able to identify stores by their ID, so we need to present each store using the only information we have: the address.

The first one we will have to solve by creating a custom SQL query that joins the necessary tables to get the store's address. The second one we will solve in a more interesting way: when for a `DynamicChoiceQuestion` Kamihi retrieves the list of choices from a datasource, it expects each row to have one or two fields. If it has one, that field is used as both the value and the label for the choice, but **if it has two fields, the first one is used as the label and the second one as the value.** This means that we can create a query that returns a formatted string with the store's address as the first field and the store's ID as the second field, and Kamihi will automatically use them as the label and value for each choice, presenting the address to the user while saving the store's ID as the selected value.

Knowing this, we can create the following query to retrieve the list of stores:

=== "`questions/store.sakila.sql`"

    ```sql
    SELECT
        printf(
            '%s, %s, %s',
            a.address,
            c.city,
            co.country
        ) AS store_address, -- (1)!
        s.store_id -- (2)!
    FROM store s
        JOIN address a ON s.address_id = a.address_id
        JOIN city c ON a.city_id = c.city_id
        JOIN country co ON c.country_id = co.country_id
    ```

    1. We format the store's address using the `printf` function to create a single string that combines the address, city, and country.
    2. We select the `store_id` as the second field, which will be used as the value for the choice.

Now we can create the question that will use this query to present the list of stores to the user. This one also has a new twist: since we cannot expect the user to remember the store address, we should instead let the user select from the available options. To do this, we can use either a custom keyboard or inline buttons. In this case, we will use a custom keyboard, since it allows for a bigger number of options to be displayed comfortably.

=== "`questions/store.py`"

    ```python
    """
    Store question type.
    """
    
    from kamihi.questions import DynamicChoice

    class Store(DynamicChoice):  # (1)!
        """
        Question type to ask for a movie title.
        """
    
        def __init__(self):
            super().__init__(
                "Please select a store location",
                request="store.sakila.sql",
                error_text="That is not one of the options. Please try again.", # (3)!
                reply_type="keyboard",  # (2)!
            )
    ```

    1. We define `Store` in the same way we did with `MovieTitle`.
    2. We set the `reply_type` to `keyboard` to use a custom keyboard for the choices.
    3. The user can still type an invalid option, so we provide an `error_text` to handle that case.

=== "questions/\_\_init\_\_.py"

    ```python
    from .movie_title import MovieTitle
    from .store import Store  # (1)!
    ```

    1. We import the new `Store` question type in the `__init__.py` file to make it available for use.

## Creating the action

As always, we create a new action with `kamihi action new favorite_store`, and then we can implement the action itself.

=== "`actions/favorite_store/favorite_store.py`"

    ```python
    """
    favorite_store action.
    """
    from kamihi import bot
    from kamihi.db import get_session
    from models import User
    from questions import Store

    @bot.action
    async def favorite_store(
        store_id: Annotated[int, Store()],
        user: User
    ) -> str:
        """
        Ask the user to select their favorite store and save it.
        """
        session = get_session()
        user.favorite_store_id = store_id  # (1)!
        session.add(user)
        session.commit()  # (2)!

        return f"Your favorite store has been set to store ID {store_id}."
    ```

    1. The action receives the `user_id` as a parameter to identify the user.
    2. We create an instance of the `Store` question and use its `ask` method to present the question to the user and get their selected store ID.
    3. We save the selected store ID to the user's `favorite_store_id` field and commit the changes to the database.
