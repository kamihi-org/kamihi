# Configuring your bot

There are three ways to configure your bot:

1. Using a configuration file
2. Using environment variables
3. Using a `.env` file
4. Directly in your code

## Configuration options

Before diving into the different methods, here are some of the most important configuration options:

- `autoreload_templates` (`KAMIHI_AUTORELOAD_TEMPLATES`): Automatically reload templates when they change (default: `true`)
- `log.stdout_level` (`KAMIHI_LOG__STDOUT_LEVEL`): Logging level for stdout (default: `INFO`)
- `log.file_enable` (`KAMIHI_LOG__FILE_ENABLE`): Enable file logging (default: `false`)
- `log.file_level` (`KAMIHI_LOG__FILE_LEVEL`): Logging level for file (default: `DEBUG`)

## Using a configuration file

The simplest way to configure your bot is by creating a configuration file. Create a file named `kamihi.yaml` in your project's root directory and add your configuration options there.

```yaml
# Basic configuration
autoreload_templates: true

# Logging configuration
log:
  stdout_level: INFO
  file_enable: true
  file_level: DEBUG
```

The configuration file will be automatically loaded when you start your bot. You can also specify a different file path by setting the `KAMIHI_CONFIG_FILE` environment variable.

## Using environment variables

You can also configure your bot using environment variables, which is useful for containerized deployments or when you need to keep sensitive information out of your code.

Environment variables for Kamihi follow the `KAMIHI_` prefix pattern. Nested configuration options use double underscores to separate levels.

```bash
# Set basic configuration
export KAMIHI_AUTORELOAD_TEMPLATES=true

# Set logging configuration (nested options)
export KAMIHI_LOG__STDOUT_LEVEL=INFO
export KAMIHI_LOG__FILE_ENABLE=true
export KAMIHI_LOG__FILE_LEVEL=DEBUG
```

## Using a `.env` file

If you prefer to use a `.env` file for environment variables, you can create a file named `.env` in your project's root directory and add your configuration options there.

```dotenv
# Basic configuration
KAMIHI_AUTORELOAD_TEMPLATES=true

# Set logging configuration (nested options)
KAMIHI_LOG__STDOUT_LEVEL=INFO
KAMIHI_LOG__FILE_ENABLE=true
KAMIHI_LOG__FILE_LEVEL=DEBUG
```

The `.env` file will be automatically loaded when you start your bot.

## Configuring in code

For the most flexibility, you can configure your bot directly in code by using the `bot.set_settings()` method.
```python
from kamihi import bot
from kamihi.base.config import KamihiSettings

# Create custom settings
settings = KamihiSettings(
    autoreload_templates=False,
    log={
        "level": "DEBUG",
        "file": "debug.log"
    }
)

# Apply settings to the bot
bot.set_settings(settings)

# Start the bot with custom settings
bot.start()
```

## Configuration priority

When multiple configuration methods are used simultaneously, Kamihi follows this priority order:

1. Direct code configuration (highest priority)
2. Environment variables
3. `.env` file
4. Configuration file (lowest priority)

This means that environment variables will override values from the configuration file, and direct code configuration will override both.

## Next Steps

Now that you've configured your bot, you're ready to start adding actions and commands. Check out the [Adding Actions](./actions.md) tutorial to learn how to make your bot respond to user commands.
