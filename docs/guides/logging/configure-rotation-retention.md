# How to Configure Log File Rotation and Retention

This guide shows you how to set up file logging with rotation and retention policies in Kamihi, preventing log files from growing too large and managing disk space efficiently.

## Prerequisites

- A Kamihi project
- Basic understanding of Kamihi's configuration system

## Available configuration options

You can configure log rotation and retention using the following options:

- **`log.file_enable`** (`KAMIHI_LOG__FILE_ENABLE`): Enable file logging
- **`log.file_path`** (`KAMIHI_LOG__FILE_PATH`): Path to the log file
- **`log.file_rotation`** (`KAMIHI_LOG__FILE_ROTATION`): Rotation policy (e.g., size, time)
- **`log.file_retention`** (`KAMIHI_LOG__FILE_RETENTION`): Retention policy (e.g., time, count)

To understand how to set configuration options, refer to the [configuration guide]().

## Common rotation patterns

Choose a rotation pattern based on your specific requirements:

- **Size-based rotation**: Rotate logs when they reach a certain size (e.g. `"100 MB"`, `"500 MB"`, `"1 GB"`)

- **Time-based rotation**: Rotate logs after a specified period (e.g. `"1 hour"`, `"1 day"`, `"1 week"`)

- **Clock-based rotation**: Rotate logs at specific times (e.g. `"00:00"` for midnight, `"sunday"` for weekly rotation)

- **Interval-based rotation**: Rotate logs at regular intervals (e.g. `"1 hour"`, `"12 hours"`)

## Common retention patterns

Choose a retention policy based on how long you need to keep your logs:

- **Time-based retention**: Keep logs for a specified period (e.g. `"10 days"`, `"1 month"`, `"1 year"`)

- **Count-based retention**: Keep a specified number of log files (e.g. `"5"`, `"10"`)

## Advanced usage

Please refer to the [`loguru` documentation](https://loguru.readthedocs.io/en/stable/api/logger.html#loguru._logger.Logger.add) for more advanced usage, including custom rotation and retention policies.
