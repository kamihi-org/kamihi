In this tutorial, you will model domain data (such as rentals) as custom database models in your Kamihi project, separate from any external datasources.

By the end of this tutorial, you will have custom SQLAlchemy models and actions that read from them, combining Kamihi DB data with datasource information when needed.

## Prerequisites

- You have completed the [Creating the bot](creating-the-bot.md) tutorial.
- You have completed the [Your first action](your-first-action.md) tutorial.
- You have completed the [Adding a datasource](adding-a-datasource.md) tutorial.
- You have completed the [Working with users and stores](working-with-users.md) tutorial.

## Designing domain data separate from datasources

- Recap the separation of concerns between external datasources and Kamihi's own DB.
- Decide which fields your domain model (e.g. `Rental`) should have.

## Creating custom models in `models/`

- Create a module under `models/` for your domain models.
- Define SQLAlchemy models linked to your user and any external identifiers.
- Optionally define related models (e.g. watchlists, favorites).

## Integrating models into the Kamihi DB

- Ensure your new models are imported so Alembic sees them.
- Generate and apply a migration for the new models.
- Verify schema changes in the database.

## Reading domain data in an action

- Create an action such as `my_rentals` or `my_items`.
- Use a Kamihi DB `Session` to query records for the current `user`.
- Enrich the results with external data from a datasource query if needed.

## Building templates for domain views

- Create `.md.jinja` templates to render domain data.
- Format the output to be clear and compact in Telegram.

## Inspecting domain data via the admin web interface

- Expose your domain model in the admin interface (if appropriate).
- Use the web UI to inspect records for test users.
- Manually adjust or delete records during development.

## TL;DR

- Design domain-specific models in your Kamihi project instead of overloading external datasources.
- Create SQLAlchemy models under `models/` and run migrations.
- Use Kamihi DB sessions in actions to query domain data for the current user.
- Optionally combine Kamihi DB data with external datasources for richer responses.
- Use the admin web interface to inspect and manage domain records.

## What's next?

In the next tutorial, you will implement actions that mutate your domain models in response to user commands, and you will introduce permissions and roles to control access.
