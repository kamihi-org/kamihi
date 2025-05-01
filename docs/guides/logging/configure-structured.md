Structured logging transforms your application logs into machine-readable JSON format instead of plain text. You should enable structured logging when:

- You need to process logs programmatically
- You're integrating with modern log management systems
- You want to enable advanced filtering and searching capabilities
- You need to track complex relationships between log events

Structured logs make it easier to analyze patterns, troubleshoot issues, and extract metrics from your application's operation.

## Prerequisites

- A Kamihi application
- Basic understanding of Kamihi configuration

## Enable structured logging

Add the appropriate configuration to your Kamihi application to enable structured logging:

=== "Config. file"
    ```yaml
    log:
      # Enable structured logging for stdout
      stdout_serialize: true

      # Enable structured logging for stderr
      stderr_enable: true
      stderr_serialize: true

      # Enable structured logging for file output
      file_enable: true
      file_path: kamihi.json
      file_serialize: true
    ```
=== "`.env` file"
    ```bash
    # Enable structured logging for stdout
    KAMIHI_LOG__STDOUT_SERIALIZE=true

    # Enable structured logging for stderr
    KAMIHI_LOG__STDERR_ENABLE=true
    KAMIHI_LOG__STDERR_SERIALIZE=true

    # Enable structured logging for file output
    KAMIHI_LOG__FILE_ENABLE=true
    KAMIHI_LOG__FILE_PATH=kamihi.json
    KAMIHI_LOG__FILE_SERIALIZE=true
    ```
=== "Programmatically"
    ```python
    from kamihi import bot
    
    bot.settings.log.stdout_serialize = True

    bot.settings.log.stderr_enable = True
    bot.settings.log.stderr_serialize = True

    bot.settings.log.file_enable = True
    bot.settings.log.file_path = "kamihi.json"
    bot.settings.log.file_serialize = True
    ```

## Checking your structured logs

When structured logging is enabled, your logs will be output as JSON objects. Each log entry will be a single line containing a JSON object that includes details like timestamp, log level, message text, and contextual information.

## Related documentation

Refer to the [Loguru documentation](https://loguru.readthedocs.io/en/stable/overview.html#structured-logging-as-needed) for more details on structured logging capabilities and how to add contextual information to your logs.
