This guide shows you how to configure and use basic logging in your Kamihi application.

If you need to capture application activity for debugging or monitoring, configure logging as described below.

## Configuring console logging

Console logging to `stdout` is enabled by default. You can configure it in several ways:

=== "kamihi.yaml"
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
    from kamihi.base.config import LogSettings, KamihiSettings

    settings = LogSettings(
        stdout_level="DEBUG"  # default is INFO
    )

    bot.set_settings(KamihiSettings(log=settings))
    ```

## Configuring `stderr` logging

If you want to log to `stderr`, you can enable and configure it similarly:

=== "kamihi.yaml"
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
    from kamihi.base.config import LogSettings, KamihiSettings
    settings = LogSettings(
        stderr_enable=True,
        stderr_level="ERROR"
    )
    bot.set_settings(KamihiSettings(log=settings))
    ```

## Adding file logging

If you need to store logs in a file:

=== "kamihi.yaml"
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
    settings = LogSettings(
        file_enable=True,
        file_path="app.log", # Path to the log file, default is "kamihi.log"
        file_level="DEBUG"
    )
    ```
