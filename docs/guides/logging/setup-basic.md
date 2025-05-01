This guide shows you how to configure and use basic logging in your Kamihi application.

If you need to capture application activity for debugging or monitoring, configure logging as described below.

## Configuring console logging

Console logging to `stdout` is enabled by default. You can configure it in several ways:

=== "Config. file"
    ```yaml
    log:
        stdout_level: DEBUG # default is INFO
    ```
=== "`.env` file"
    ```bash
    KAMIHI_LOG__STDOUT_LEVEL=DEBUG # default is INFO
    ```
=== "Programmatically"
    ```python
    from kamihi import bot

    # Set the logging level for stdout
    bot.settings.log.stdout_level = "DEBUG"  # default is INFO
    ```

## Configuring `stderr` logging

If you want to log to `stderr`, you can enable and configure it similarly:

=== "Config. file"
    ```yaml
    log:
        stderr_enable: true
        stderr_level: ERROR
    ```
=== "`.env` file"
    ```bash
    KAMIHI_LOG__STDERR_ENABLE=true
    KAMIHI_LOG__STDERR_LEVEL=ERROR
    ```
=== "Programmatically"
    ```python
    from kamihi import bot

    # Enable and set the logging level for stderr
    bot.settings.log.stderr_enable = True
    bot.settings.log.stderr_level = "ERROR"
    ```

## Adding file logging

If you need to store logs in a file:

=== "Config. file"
    ```yaml
    log:
        file_enable: true
        file_path: app.log # Path to the log file, default is "kamihi.log"
        file_level: DEBUG
    ```
=== "`.env` file"
    ```bash
    KAMIHI_LOG__FILE_ENABLE=true
    KAMIHI_LOG__FILE_PATH=app.log # Path to the log file, default is "kamihi.log"
    KAMIHI_LOG__FILE_LEVEL=DEBUG
    ```
=== "Programmatically"
    ```python
    from kamihi import bot

    # Enable file logging and set the log file path and level
    bot.settings.log.file_enable = True
    bot.settings.log.file_path = "app.log"  # Path to the log file, default is "kamihi.log"
    bot.settings.log.file_level = "DEBUG"
    ```
