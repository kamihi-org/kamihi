In this tutorial, you will use Kamihi's job scheduling features to automate actions based on time, such as sending periodic recommendations or reminders.

By the end of this tutorial, you will have scheduled jobs that invoke your actions at regular intervals, targeting specific users or roles.

## Prerequisites

- You have completed the [Creating the bot](creating-the-bot.md) tutorial.
- You have completed the [Your first action](your-first-action.md) tutorial.
- You have completed the [Adding a datasource](adding-a-datasource.md) tutorial.
- You have completed the [Working with users and stores](working-with-users-and-stores.md) tutorial.
- You have completed the [Modeling domain data](modeling-domain-data.md) tutorial.
- You have completed the [Mutating domain data](mutating-domain-data.md) tutorial.
- You have completed the [Sending media](sending-media.md) tutorial.

## Enabling jobs in configuration

- Explain the `jobs.enabled` setting in `kamihi.yaml`.
- Show how to toggle jobs via environment variables.
- Restart the bot and confirm jobs are enabled in logs.

## Designing scheduled actions

- Define the purpose of your scheduled actions (e.g. recommendations, reminders).
- Ensure actions can be called by commands and by jobs.

## Implementing actions suitable for jobs

- Implement actions that accept arguments via JSON from jobs.
- Make sure they behave correctly when invoked without user interaction.

## Creating jobs in the admin web interface

- Walk through creating jobs for your scheduled actions.
- Choose users and roles, configure `per_user`, and set cron expressions.
- Provide arguments as JSON where required.

## Understanding `per_user`, `user`, and `users`

- Explain how `per_user` affects the `user` parameter.
- Show how `users` is populated when `per_user` is disabled.
- Demonstrate patterns for writing actions that work in both contexts.

## Testing and monitoring jobs

- Use the admin web interface to run jobs manually.
- Inspect logs to verify correct execution and error handling.
- Consider performance and rate limiting when targeting many users.

## TL;DR

- Enable jobs in `kamihi.yaml` and restart your bot.
- Implement actions that can be invoked by jobs with JSON arguments.
- Create and manage jobs from the admin web interface using cron expressions.
- Understand how `per_user` affects the `user` and `users` parameters.

## What's next?

In the final tutorial, you will prepare your Kamihi project for production by hardening configuration, logging, permissions, and deployment.
