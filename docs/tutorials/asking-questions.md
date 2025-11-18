In this tutorial, you will learn how to employ reusable questions in your actions to get information from the user. This will enhance your bot's interactivity and allow it to gather necessary data seamlessly.

By the end of this tutorial, you will have created an action that asks the user for a movie title, and returns the details of that movie from the Sakila database.

## Reusable questions

Kamihi provides a convenient way to ask users questions and handle their responses through reusable questions. This feature allows you to define a question once and use it across multiple actions, ensuring consistency and reducing redundancy.

Kamihi already has some built-in questions that we can use. You can check out the list of available questions in the [questions guide](../guides/actions/ask-questions.md).

In this tutorial we will be using some of these built-in questions to ask the user for a movie title.

## Creating the `details` action

Let's create a new action called `details` that will ask the user for a movie title and return the details of that movie from the Sakila database. You should already know how to do it, but just in case, I'll show you again. Run the following command:

<!-- termynal -->
```shell
> kamihi action new details
Copying from template version x.x.x
 identical  actions
    create  actions/details
    create  actions/details/details.py
    create  actions/details/__init__.py

```

Now let's create a SQL query file that will retrieve the movie details based on the title provided by the user. Create a new file called `details.sakila.sql` under the `actions/details` folder with the following content:

