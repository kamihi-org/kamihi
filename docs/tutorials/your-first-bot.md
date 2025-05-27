## Prerequisites

To start using Kamihi, you will need three things installed on your machine:

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

- `docker` and (optionally) `docker compose`: to deploy the database for Kamihi. Te easiest way to install it is through [Docker Desktop](https://docs.docker.com/desktop/), especially if you are on Windows. Otherwise, you can install the [Docker Engine](https://docs.docker.com/engine/install/) and [Docker Compose](https://docs.docker.com/compose/install/) directly. Any version is fine, as long as you call Docker Compose with `docker compose` (as opposed to `docker-compose`). Test your installation by running:
    <!-- termynal -->
    ```shell
    > docker --version
    Docker version 27.5.1, build 3.fc42
    > docker compose version
    Docker Compose version v2.24.2
    ```

## Creating your project

To create a new bot using Kamihi, run the following command:

<!-- termynal -->
```
> uvx kamihi init hello-world
Copying from template version x.x.x
    create  pyproject.toml
    ...    
```

This will create a folder named `hello-world` in your current directory and create all the necessary files. You fill find the following files:

``` yaml
hello-world/
├── actions # (1)!
│   └── start # (2)!
│       ├── \_\_init\_\_.py
│       └── start.py
├── docker-compose.dev.yml
├── docker-compose.yml
├── .dockerignore
├── .gitignore
├── Dockerfile
├── kamihi.yml # (3)!
├── models # (4)!
│   └── user.py
├── pyproject.toml # (5)!
├── .python-version
└── README.md
```

1. The actions folder. This is where you'll spend most of your time. It holds all the things you can do with the bot.
2. A sample action, free of charge ;)
3. The configuration file for Kamihi
4. The directory for database models, where you can customize the default ones and add more.
5. The Python project file.

Don't worry if you are not sure what all files do. The base project is designed to work out of the box.

Get into the project and install all dependencies by running these two commands:

<!-- termynal -->
```bash
> cd hello-world
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
---

token: YOUR_TOKEN_HERE # (1)!
timezone: UTC # Timezone for the bot


# Templates are auto-reloaded by default, uncomment to disable
# autoreload_templates: false
```

1. Right here, substituting `YOUR_TOKEN_HERE`

## Starting the database

Kamihi runs on top of MongoDB, so before we start doing things with our bot, we need to start it.

There are many ways to deploy MongoDB, but for this tutorial, we will use Docker as it is a matter of one command:

=== "Docker"

    <!-- termynal -->
    ```bash
    > docker run -d \
        --name mongodb \
        --restart unless-stopped \
        -p 27017:27017 \
        -v /data/db \
        mongo:latest
    (returns a big hash code)
    ```

=== "Docker Compose"

    <!-- termynal -->
    ```bash
    > docker compose -f docker-compose.dev.yml up mongodb -d
    ---> 100%
    [+] Running 1/1
    ✔ Container mongodb  Started
    ```

## Creating our first user

Last but not least, before we start the bot, we need to register our fist user. For that, we need our account's ID, which you can obtain by messaging [this bot](https://t.me/myidbot) on Telegram.

We will add this first user as an administrator, so it will have permission to use all actions. Later we will see how we can customize each user's permissions.

To add it, we just need to run this command (substituting `user_id` with your actual Telegram ID):

<!-- termynal -->
```shell
> kamihi user add user_id --admin
2025-01-01 at 00:00:00 | SUCCESS  | User added. telegram_id=<your_user_id>, is_admin=True
```

## Running the bot

We are now ready to start our bot for the first time! To do so, just run this command in the root of your project:

<!-- termynal -->
```shell
> kamihi run
2025-01-01 at 00:00:00 | INFO     | Web server started on http://localhost:4242 host='localhost', port=4242
2025-01-01 at 00:00:00 | SUCCESS  | Started!

```

You can now go to Telegram and start a conversation with your bot by sending the command `/start`.

![Sending the `/start` command](../images/tutorials-your-first-bot-start.png)

## What now?

Now that you have a basic bot up and running, you can start adding some actions to it. We have just scratched the surface of what you can do with Kamihi. Check out the [next tutorial](adding-actions.md) on how to add more actions, or the [guides](../guides/index.md) for more in-depth information on how to use Kamihi to the fullest.
