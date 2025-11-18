In this tutorial, you will use Kamihi's media helpers to send static media files such as images, documents, and videos to your users.

By the end of this tutorial, you will have actions that send media using both implicit and explicit media types, with captions rendered from templates.

## Prerequisites

- You have completed the [Creating the bot](creating-the-bot.md) tutorial.
- You have completed the [Your first action](your-first-action.md) tutorial.
- You have completed the [Adding a datasource](adding-a-datasource.md) tutorial.
- You have completed the [Working with users and stores](working-with-users-and-stores.md) tutorial.
- You have completed the [Modeling domain data](modeling-domain-data.md) tutorial.
- You have completed the [Mutating domain data](mutating-domain-data.md) tutorial.

## Planning your media strategy

- Decide which media you want to support (images, documents, videos).
- Set up a `static/` folder in your project to hold media files.
- Define a mapping from domain identifiers to media filenames if needed.

## Sending media with implicit and explicit types

- Create an action that returns a `Path` to send media implicitly.
- Create an action that uses explicit `bot.*` media types (e.g. `bot.Photo`, `bot.Document`).
- Discuss when each approach is preferable.

## Sending multiple media items and groups

- Add examples of sending multiple media files.
- Show how to send media groups when appropriate.

## Adding captions with templates

- Use templates to generate captions that include domain data.
- Apply captions to single media items and media groups.

## Integrating media into existing actions

- Extend existing actions to include media without changing business logic.

## Using the admin web interface to support media

- Optionally expose a model mapping IDs to media paths for admin editing.
- Use the admin web to inspect any media-related models.

## TL;DR

- Organize static media files under a `static/` folder.
- Use `Path` or `bot.*` media classes to send images, documents, and videos.
- Combine media with templates to provide informative captions.
- Integrate media into existing actions without changing datasource behavior.

## What's next?

In the next tutorial, you will use Kamihi's job scheduling features to automate actions, such as sending recommendations and reminders.
