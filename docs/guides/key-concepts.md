These are the most important concepts and definitions used throughout this documentation.

## Action

An action is, in its most basic terms, something you can do with your bot. You are in charge of defining them.

## Command

A command is a string sent to your bot through Telegram that executes an action. They are always prefixed with a slash (for example, `/start` or `/hello`). 

!!! info
    An action may have many commands assigned.

## User

A user is someone that has been registered in the framework. Only they can use the actions you define.

## Role

A role is, in essence, a group of users. Roles are most commonly used to grant them permission to use actions. Many users can have one role, and users can also have many roles.

## Permission

A permission is a record that tells the bot which users and roles can use which actions. You can have many permissions for each action, each targeting as many users and roles as you want.
