This guide explains how to load configuration settings for your Kamihi application from a file. Using a configuration file allows you to easily manage and modify settings without altering your code.

## Prerequisites

- A Kamihi project.
- A basic understanding of Kamihi's configuration system.

## Configuration basics

Kamihi supports loading configuration from YAML files. By default, it looks for a file named `kamihi.yaml` in the same directory as your application. You can also specify a custom file path using the `KAMIHI_CONFIG_FILE` environment variable.

The configuration file should contain settings that correspond to the attributes defined in your `KamihiSettings` class.

## Steps

1.  **Create a configuration file:**

    Create a file named `kamihi.yaml` (or choose a different name) in your project directory. Add your desired configuration settings to this file. For example:

    ```yaml
    log:
      stdout_level: DEBUG
      file_enable: true
      file_path: "app.log"
    ```

2.  **Specify the configuration file (optional):**

    If you are not using the default `kamihi.yaml` file, set the `KAMIHI_CONFIG_FILE` environment variable to the path of your configuration file. This can be done in your shell or in a `.env` file:

    === "Environment variable"
        ```bash
        export KAMIHI_CONFIG_FILE=/path/to/your/config.yaml
        ```

    === "`.env` file"
        ```env
        KAMIHI_CONFIG_FILE=/path/to/your/config.yaml
        ```

3.  **Load the settings:**

    When your Kamihi application starts, it will automatically load the configuration from the specified file (or the default `kamihi.yaml` if no environment variable is set).  You can then access these settings through `bot.settings`.

    ```python
    from kamihi import bot

    print(bot.settings.log.stdout_level)  # Output: DEBUG
    ```

## Notes

-   Settings in the configuration file will override the default values defined in your `KamihiSettings` class.
-   Environment variables (e.g., `KAMIHI_LOG__STDOUT_LEVEL`) will take precedence over settings in the configuration file.
-   If the file specified by `KAMIHI_CONFIG_FILE` does not exist, Kamihi will fall back to the default `kamihi.yaml` file, or to the default settings if that file doesn't exist either.
