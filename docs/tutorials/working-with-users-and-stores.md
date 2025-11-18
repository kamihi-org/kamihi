In this tutorial, you will extend Kamihi's user model with custom fields and use questions plus datasources to let users choose and persist their favorite store.

By the end of this tutorial, you will have used the framework's user extension, questions, and database integration features to store a per-user preference and act on it.

## Prerequisites

- You have completed the [Creating the bot](creating-the-bot.md) tutorial.
- You have completed the [Your first action](your-first-action.md) tutorial.
- You have completed the [Adding a datasource](adding-a-datasource.md) tutorial and can list films or stores.

## Designing user-specific data

- Explain why some data belongs to the user model rather than an external datasource.
- Clarify that favorite store must be stored in the Kamihi DB, not in the Sakila datasource.
- Describe how user data influences later actions (availability checks, recommendations).

## Extending the user model

- Review the default user model created during project initialization.
- Follow the "extend user" guide to add a `favorite_store_id` field.
- Run migrations to apply the change to the Kamihi DB.

## Fetching stores from a datasource

- Create an action (e.g. `choose_store`) to let users select a store.
- Add a SQL file that retrieves the list of stores from the datasource.
- Use that query to build options for the user.

## Asking the user to select a store

- Use `Choice` or `DynamicChoice` questions to present the store list.
- Design the action's flow to handle user selection.

## Saving user preferences in Kamihi DB

- Use a `Session` on the Kamihi DB to update the user's `favorite_store_id`.
- Ensure that the change is committed correctly.
- Handle the case where the user changes their favorite store.

## Sending store locations as `Location`

- Define a mapping from store IDs to geographic coordinates.
- Use `bot.Location` to send a Telegram location for the selected store.
- Optionally reuse this in other actions to show the user's preferred store.

## Using the admin web interface along the way

- Verify that user records contain the `favorite_store_id`.
- Optionally edit a user's favorite store through the admin interface.
- Use the admin view to sanity-check the changes.

## TL;DR

- Extend the Kamihi user model to add a custom field such as `favorite_store_id`.
- Build an action that lists stores from a datasource and lets users choose one.
- Save the choice to the user's data using a Kamihi DB session.
- Use Kamihi's media helpers to send a Telegram `Location` pointing to the store.
- Confirm the results using the admin web interface.

## What's next?

In the next tutorial, you will introduce custom models to represent rentals and other domain concepts in the Kamihi database, while keeping external datasources read-only.
