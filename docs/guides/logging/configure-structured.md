This guide shows you how to enable structured logging in Kamihi to generate machine-readable log output in JSON format, which is useful for log aggregation and analysis tools.

## Prerequisites

- A Kamihi application
- Basic understanding of Kamihi configuration

## Enable structured logging

Add the appropriate configuration to your Kamihi application to enable structured logging:

=== "kamihi.yaml"
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
    from kamihi.base.config import LogSettings, KamihiSettings

    settings = LogSettings(
        # Enable structured logging for stdout
        stdout_serialize=True,

        # Enable structured logging for stderr
        stderr_enable=True,
        stderr_serialize=True,

        # Enable structured logging for file output
        file_enable=True,
        file_path="kamihi.json",
        file_serialize=True
    )
    bot.set_settings(KamihiSettings(log=settings))
    ```

## Checking your structured logs

When structured logging is enabled, your logs will be output as JSON objects. Each log entry will be a single line containing a JSON object.

For stdout/stderr logs, they'll appear in your terminal as JSON strings:

```json
{
  "text": "This is an info message", // (1)!
  "record": { // (2)!
      "microseconds": 63979, 
      "seconds": 0.063979
    }, 
    "exception": null, // (3)!
    "extra": {}, // (4)!
    "file": {
      "name": "example.py", 
      "path": "/path/to/example.py"
    }, 
    "function": "main", 
    "level": {
      "icon": "ℹ️", 
      "name": "INFO", 
      "no": 20
    }, 
    "line": 10, 
    "message": "This is an info message", 
    "module": "example", 
    "name": "root",
    "process": {
      "id": 12345, 
      "name": "MainProcess"
    }, 
    "thread": {
      "id": 140735, 
      "name": "MainThread"
    }, "time": {
      "timestamp": 1633000000.0
    }
  }
}
```

1. The plain text of the log message is still included in the `text` field for easy readability.
2. The `record` field contains all the structured information about the log entry.
3. If an exception occurred, it will be included in the `exception` field with detailed information.
4. The `extra` field contains any additional context you added to the log entry. Refer to the [`loguru` documentation](https://loguru.readthedocs.io/en/stable/overview.html#structured-logging-as-needed) for more details on how to add extra data.

For file logs with serialization enabled, each line in your log file will be a JSON object with the same structure.

## Common usage scenarios

- If you need to feed logs to ELK Stack (Elasticsearch, Logstash, Kibana)
- If you use log aggregation services like Datadog, Splunk, or Graylog
- If you want to perform automated analysis or filtering of logs
- If you need to search or query logs programmatically

By configuring structured logging, you ensure your log data can be easily processed by these systems.

## Related documentation

Refer to the [Loguru documentation](https://loguru.readthedocs.io/en/stable/overview.html#structured-logging-as-needed) for more details on structured logging capabilities.
