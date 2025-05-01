This guide shows you how to set up file logging with rotation and retention policies in Kamihi, preventing log files from growing too large and managing disk space efficiently.

## Prerequisites

- A Kamihi project
- Basic understanding of Kamihi's configuration system

## Configuration basics

Kamihi uses the following configuration options for log rotation and retention:

- **`log.file_enable`** (`KAMIHI_LOG__FILE_ENABLE`): Enable file logging
- **`log.file_path`** (`KAMIHI_LOG__FILE_PATH`): Path to the log file
- **`log.file_rotation`** (`KAMIHI_LOG__FILE_ROTATION`): Rotation policy
- **`log.file_retention`** (`KAMIHI_LOG__FILE_RETENTION`): Retention policy

To understand how to set configuration options, refer to the [configuration guide]().

## Common logging scenarios

### High-volume production applications

If your application produces high-volume logs (e.g., many requests per second), the following settings are recommended

=== "Config. file"
    ```yaml
    log:
    file_enable: true
    file_path: "/var/log/kamihi/app.log"
    file_rotation: "100 MB" # Rotate when the file reaches 100 MB
    file_retention: "10 days" # Keep logs for 10 days
    ```
=== "`.env` file"
    ```bash
    KAMIHI_LOG__FILE_ENABLE=true
    KAMIHI_LOG__FILE_PATH="/var/log/kamihi/app.log"
    KAMIHI_LOG__FILE_ROTATION="100 MB" # Rotate when the file reaches 100 MB
    KAMIHI_LOG__FILE_RETENTION="10 days" # Keep logs for 10 days
    ```
=== "Programmatically"
    ```python
    from kamihi import bot

    bot.settings.log.file_enable = True
    bot.settings.log.file_path = "/var/log/kamihi/app.log"
    bot.settings.log.file_rotation = "100 MB"  # Rotate when the file reaches 100 MB
    bot.settings.log.file_retention = "10 days"  # Keep logs for 10 days
    ```

Alternatively, for containers or environments with limited disk space, you can use a more conservative approach:

=== "Config. file"
    ```yaml
    log:
    file_enable: true
    file_path: "/var/log/kamihi/app.log"
    file_rotation: "50 MB" # Rotate when the file reaches 50 MB
    file_retention: "3 days" # Keep logs for 3 days
    ```
=== "`.env` file"
    ```bash
    KAMIHI_LOG__FILE_ENABLE=true
    KAMIHI_LOG__FILE_PATH="/var/log/kamihi/app.log"
    KAMIHI_LOG__FILE_ROTATION="50 MB" # Rotate when the file reaches 50 MB
    KAMIHI_LOG__FILE_RETENTION="3 days" # Keep logs for 3 days
    ```
=== "Programmatically"
    ```python
    from kamihi import bot

    bot.settings.log.file_enable = True
    bot.settings.log.file_path = "/var/log/kamihi/app.log"
    bot.settings.log.file_rotation = "50 MB"  # Rotate when the file reaches 50 MB
    bot.settings.log.file_retention = "3 days"  # Keep logs for 3 days
    ```

### Background or batch processing applications

If your application runs scheduled jobs or processes data in batches, you can configure daily rotation to match your job schedule:

=== "Config. file"
    ```yaml
    log:
    file_enable: true
    file_path: "/var/log/kamihi/app.log"
    file_rotation: "1 day" # Rotate daily
    file_retention: "7 days" # Keep logs for 7 days
    ```
=== "`.env` file"
    ```bash
    KAMIHI_LOG__FILE_ENABLE=true
    KAMIHI_LOG__FILE_PATH="/var/log/kamihi/app.log"
    KAMIHI_LOG__FILE_ROTATION="1 day" # Rotate daily
    KAMIHI_LOG__FILE_RETENTION="7 days" # Keep logs for 7 days
    ```
=== "Programmatically"
    ```python
    from kamihi import bot

    bot.settings.log.file_enable = True
    bot.settings.log.file_path = "/var/log/kamihi/app.log"
    bot.settings.log.file_rotation = "1 day"  # Rotate daily
    bot.settings.log.file_retention = "7 days"  # Keep logs for 7 days
    ```

### Development environments

For local development, we do not recommend using file logging, as it can clutter your workspace. However, if you want to keep logs for debugging purposes, you can set a short retention period:

=== "Config. file"
    ```yaml
    log:
    file_enable: true
    file_path: "app.log"
    file_rotation: "1 hour" # Rotate every hour
    file_retention: "1 day" # Keep logs for 1 day
    ```
=== "`.env` file"
    ```bash
    KAMIHI_LOG__FILE_ENABLE=true
    KAMIHI_LOG__FILE_PATH="app.log"
    KAMIHI_LOG__FILE_ROTATION="1 hour" # Rotate every hour
    KAMIHI_LOG__FILE_RETENTION="1 day" # Keep logs for 1 day
    ```
=== "Programmatically"
    ```python
    from kamihi import bot

    bot.settings.log.file_enable = True
    bot.settings.log.file_path = "app.log"
    bot.settings.log.file_rotation = "1 hour"  # Rotate every hour
    bot.settings.log.file_retention = "1 day"  # Keep logs for 1 day
    ```

## Advanced usage

Please refer to the [`loguru` documentation](https://loguru.readthedocs.io/en/stable/api/logger.html#loguru._logger.Logger.add) for more advanced usage, including custom rotation and retention policies.
