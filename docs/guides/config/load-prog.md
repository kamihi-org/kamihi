This guide explains how to configure your Kamihi application programmatically. This method is useful when you need to dynamically generate or modify configuration settings within your code.

## Prerequisites

-   A Kamihi project.
-   A basic understanding of Kamihi's configuration system.

## Configuration basics

Kamihi allows you to configure settings directly in your Python code by instantiating and modifying the `KamihiSettings` class. This approach bypasses the need for environment variables or configuration files, providing greater flexibility for dynamic configurations.

## Steps

1. **Import the bot instance:** 
   ```python
   from kamihi import bot
   ```
2. **Set the desired settings programmatically:** You can set the desired settings directly on the `bot.settings` object. For example:
    ```python
    bot.settings.log.stdout_level = "DEBUG"
    bot.settings.log.file_enable = True
    bot.settings.log.file_path = "app.log"
    ```

## Notes

-   Programmatically set settings will override default values and settings loaded from configuration files or environment variables.
-   Configuration changes made programmatically will not be validated against the schema defined in the `KamihiSettings` class. Ensure that the values you set are valid according to the expected types and formats.
-   This method is ideal for scenarios where configuration needs to be determined at runtime based on application logic or external factors.
