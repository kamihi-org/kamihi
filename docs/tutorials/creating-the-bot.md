In this first tutorial, we will go through the steps needed to create a new bot using Kamihi, and get it up and running. 

By the end of this tutorial, you will have a basic bot that can respond to the `/start` command.

## Prerequisites

You will need two things installed on your machine:

- `git`: a version control manager. You can find installation instructions [here](https://git-scm.com/downloads), although if you are using Linux, you probably have it. To check your installation, you can use the following command on your terminal of choice:
      <!-- termynal -->
      ```bash
      > git -v
      git version 2.49.0
      ```
      The version does not matter, any is fine as long as it shows.

- `uv`: a Python package manager. For instructions on installing, you can follow [this guide](https://docs.astral.sh/uv/getting-started/installation/). To verify you have correctly installed it, run this command (any version is fine too):
    <!-- termynal -->
    ```bash
    > uv --version
    uv 0.7.6
    ```
    If you do not want to use `uv`, refer to the [guide for other package managers](../guides/projects/other-package-managers.md).

## Creating your project

To create our new bot using Kamihi, run the command `uvx kamihi init <name>`, substituting `<name>` with the name you want for your project. For this tutorial, we will use `rentals`:

<!-- termynal -->
```
> uvx kamihi init rentals
Copying from template version x.x.x
    create  pyproject.toml
    ...    
```

This will create a folder named `rentals` in your current directory and create all the necessary files. You fill find the following files:

``` yaml
rentals/
├── actions # (1)!
│   └── start # (2)!
│       ├── __init__.py
│       └── start.py
├── migrations # (6)!
│   ├── versions/
│   ├── __init__.py
│   ├── script.py.mako
│   └── env.py
├── models # (4)!
│   └── user.py
├── docker-compose.dev.yml
├── docker-compose.yml
├── .dockerignore
├── .gitignore
├── Dockerfile
├── kamihi.yml # (3)!
├── pyproject.toml # (5)!
├── .python-version
└── README.md
```

1. The actions folder. This is where you'll spend most of your time. It holds all the things you can do with the bot.
2. A sample action, free of charge ;)
3. The configuration file for Kamihi
4. The directory for database models, where you can customize the default ones and add more.
5. The Python project file.
6. The database migrations folder, which is used to keep track of changes to the database schema.

Don't worry if you are not sure what all files do. The base project is designed to work out of the box.

Get into the project and install all dependencies by running these two commands:

<!-- termynal -->
```bash
> cd rentals
> uv sync
Using CPython 3.12.10
Creating virtual environment at: .venv
Resolved 46 packages
Prepared 2 packages
---> 100%
Done!
```

## Getting your token

Before we start doing things with our bot, we need a token. This token is a unique identifier for a bot and is used to authenticate it with the Telegram API. You can get a token by talking to [@BotFather](https://t.me/botfather) on Telegram. Just send him the `/newbot` command and follow the instructions. He'll give you a token that looks something like this:

```
123456789:ABC-DEF1234ghIkl-zyx57W2P0s
```

We can input our token in the configuration file we saw before (`kamihi.yml`) so that Kamihi can use it. Go ahead and open that file, and paste it in place of `YOUR_TOKEN_HERE`. Leave the rest alone, we'll come back to it later.

```yaml
# Kamihi configuration file

token: YOUR_TOKEN_HERE # (1)!
timezone: UTC
```

1. Right here, substituting `YOUR_TOKEN_HERE`

??? warning "Keep your token safe!"

    Never share your bot's token with anyone. If someone else gets access to it, they can control your bot and potentially misuse it. If you think your token has been compromised, you can always regenerate it using BotFather.

    In fact, the whole `kamihi.yml` file can contain sensitive information (like database passwords), so you should keep it safe and avoid sharing it publicly.

While you are at it, send a message to your bot on Telegram (the default `/start` command works fine) so that it is aware of your existence when we start it later. Otherwise, we will encounter some errors later because a bot cannot message users that have not interacted with it first.

## Creating the database

Kamihi runs on top of SQLAlchemy and Alembic so it can use a database to store its data. For development purposes, we can use SQLite, which is a file-based database that requires no setup. To start the database, we just need to run the following two commands:

<!-- termynal -->
```shell
> kamihi db migrate
2025-01-01 at 00:00:007 | SUCCESS  | Migrated

> kamihi db upgrade
2025-01-01 at 00:00:007 | SUCCESS  | Upgraded
```

This will create a file named `kamihi.db` in the root of your project, which is the SQLite database file. It will also create a file in the `migrations/versions` folder, which contains the database schema.

??? info "What are migrations?"

    Migrations are a way to keep track of changes to the database schema over time. Whenever we change the database models, we need to create a new migration to apply those changes to the database with `kamihi db migrate` and apply it to the database with `kamihi db upgrade`. Kamihi uses [Alembic](https://alembic.sqlalchemy.org/en/latest/) under the hood to manage migrations.

## Creating our first user

Last but not least, before we start the bot, we need to register our fist user. For that, we need our account's ID, which you can obtain by messaging [this bot](https://t.me/myidbot) on Telegram.

We will add this first user as an administrator, so it will have permission to use all actions. Later we will see how we can customize each user's permissions.

To add it, we just need to run this command (substituting `<user_id>` with your actual Telegram ID):

<!-- termynal -->
```shell
> kamihi user add --admin <user_id>
2025-01-01 at 00:00:00 | SUCCESS  | User added
```

## Running the bot

We are now ready to start our bot for the first time! To do so, just run this command in the root of your project:

<!-- termynal -->
```shell
> kamihi run
2025-01-01 at 00:00:00 | SUCCESS     | Admin interface started on http://localhost:4242
2025-01-01 at 00:00:00 | SUCCESS  | Bot started

```

If you go to Telegram, you will see that the bot has answered your `/start` command:

![Sending the `/start` command](../images/tutorials-your-first-bot-start.png)

## TL;DR

Here is a summary of the steps we took to create our first bot:

1. Created a new Kamihi project with `uvx kamihi init <name>`.
2. Installed dependencies with `uv sync`.
3. Got a bot token from BotFather and added it to `kamihi.yml`.
4. Created the database with `kamihi db migrate` and `kamihi db upgrade`.
5. Added our first user as an admin with `kamihi user add --admin <user_id>`.
6. Ran the bot with `kamihi run`.

## What now?

Now that you have a basic bot up and running, you can start adding some actions to it. We have just scratched the surface of what you can do with Kamihi. Check out the [next tutorial](your-first-action.md) on how to add more actions, or the [guides](../guides/index.md) for more in-depth information on how to use Kamihi to the fullest.
