This guide explains how to load configuration settings for your Kamihi application from environment variables. Using environment variables allows you to configure your application in different environments without modifying your code or configuration files.

## Prerequisites

-   A Kamihi project.
-   A basic understanding of Kamihi's configuration system.

## Configuration basics

Kamihi automatically loads configuration settings from environment variables.  Environment variables must be prefixed with `KAMIHI_` to be recognized by the Kamihi configuration system. Nested settings are defined using double underscores `__`. For example, the `stdout_level` attribute within the `log` section would be represented by the environment variable `KAMIHI_LOG__STDOUT_LEVEL`.

The environment variables correspond to the attributes defined in the `KamihiSettings` class.

## Steps

1.  **Define environment variables:**

    Set the desired environment variables in your shell or in a `.env` file. For example:

    === "Environment variables"

        ```bash
        export KAMIHI_LOG__STDOUT_LEVEL=DEBUG
        export KAMIHI_LOG__FILE_ENABLE=true
        export KAMIHI_LOG__FILE_PATH="app.log"
        ```

    === "`.env` file"

        ```env
        KAMIHI_LOG__STDOUT_LEVEL=DEBUG
        KAMIHI_LOG__FILE_ENABLE=true
        KAMIHI_LOG__FILE_PATH="app.log"
        ```

2.  **Load the settings:**

    The Kamihi framework will automatically load the configuration from the environment variables. You can then access these settings through `bot.settings`.

    ```python
    from kamihi import bot

    print(bot.settings.log.stdout_level)  # Output: DEBUG
    ```

## Notes

-   Environment variables will override the default values defined in the `KamihiSettings` class.
-   Environment variables take precedence over settings in a configuration file.
-   Changes to environment variables require a restart of the Kamihi application to take effect.
