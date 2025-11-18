In this tutorial, you will implement actions that modify your domain models in response to user commands, and use Kamihi's permissions and roles system to control who can perform those operations.

By the end of this tutorial, you will have actions that create and update records in the Kamihi DB, and you will have basic roles and permissions configured to protect them.

## Prerequisites

- You have completed the [Creating the bot](creating-the-bot.md) tutorial.
- You have completed the [Your first action](your-first-action.md) tutorial.
- You have completed the [Adding a datasource](adding-a-datasource.md) tutorial.
- You have completed the [Working with users and stores](working-with-users-and-stores.md) tutorial.
- You have completed the [Modeling domain data](modeling-domain-data.md) tutorial.

## Designing mutation flows

- Define the user journey for mutating domain data (e.g. creating and closing rentals).
- Clarify which checks rely on external datasources and which updates happen in the Kamihi DB.

## Implementing actions that create records

- Implement an action that creates a new domain record using a Kamihi DB `Session`.
- Use questions where needed to gather parameters.
- Commit the changes and confirm success to the user.

## Implementing actions that update records

- Implement an action that lets the user select an existing record (e.g. from a list).
- Apply updates to the selected record in the Kamihi DB.
- Confirm success with a template-based message.

## Introducing roles and permissions

- Define roles such as regular users and managers.
- Use the Kamihi CLI and admin web interface to create roles and assign them to users.
- Configure permissions for your mutating actions.

## Templates for confirmations and errors

- Create templates for success and error messages.
- Provide clear feedback when operations cannot proceed.

## Verifying behavior in the admin web interface

- Use the admin web to inspect records before and after operations.
- Confirm that roles and permissions are configured as intended.

## TL;DR

- Implement actions that create and update domain data using Kamihi DB sessions.
- Use questions to gather input and templates for user feedback.
- Configure roles and permissions to control who can perform mutations.
- Verify behavior and permissions via the admin web interface.

## What's next?

In the next tutorial, you will enrich your bot with static media files and learn how to send them using Kamihi's media helpers.
