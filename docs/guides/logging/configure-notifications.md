This guide shows you how to set up log notifications in Kamihi to receive alerts for important log events through various notification services.

## Prerequisites

- A Kamihi application
- Access to one or more notification services (Discord, Slack, Email, Telegram, etc.)
- Basic understanding of log levels

## Configure notification logging

Add the appropriate configuration to your Kamihi application to enable notification logging:

=== "Config. file"
    ```yaml
    log:
      # Enable notification logging
      notification_enable: true
      
      # Set the minimum log level that triggers notifications
      notification_level: ERROR
      
      # Add notification service URLs (Apprise format)
      notification_urls:
        - discord://webhook_id/webhook_token
        - slack://token/channel
        - telegram://bot_token/chat_id
    ```
=== "`.env` file"
    ```bash
    # Enable notification logging
    KAMIHI_LOG__NOTIFICATION_ENABLE=true
    
    # Set the minimum log level that triggers notifications
    KAMIHI_LOG__NOTIFICATION_LEVEL=ERROR
    
    # Add notification service URLs (Apprise format)
    # For multiple URLs, use comma-separated values
    KAMIHI_LOG__NOTIFICATION_URLS=discord://webhook_id/webhook_token,slack://token/channel
    ```
=== "Programmatically"
    ```python
    from kamihi import bot

    bot.settings.log.notification_enable = True
    bot.settings.log.notification_level = "ERROR"
    bot.settings.log.notification_urls = [
        "discord://webhook_id/webhook_token",
        "slack://token/channel",
        "telegram://bot_token/chat_id"
    ]
    ```

## Setting up notification services

## Telegram

You can use the same Telegram bot token and chat ID that you use for the main bot. To set up notifications:

1. Get your bot token
2. Get your chat ID (you can use the `getUpdates` method to find it)
3. Use the format: `telegram://bot_token/chat_id`

### Discord

To set up Discord notifications:

1. In your Discord server, go to **Server Settings** > **Integrations** > **Webhooks**
2. Click **New Webhook**, give it a name and select a channel
3. Click **Copy Webhook URL**
4. Use this URL in the format: `discord://webhook_id/webhook_token`

### Slack

To set up Slack notifications:

1. Create a Slack app at https://api.slack.com/apps
2. Enable **Incoming Webhooks** for your app
3. Add a new webhook to your workspace
4. Copy the webhook URL
5. Use this URL in the format: `slack://token/channel`

### Email

To set up email notifications:

1. Use the format: `mailto://user:password@gmail.com`
2. For Gmail, you may need to create an app password

### Other services

Please refer to the [Apprise documentation](https://github.com/caronc/apprise/blob/master/README.md) for more information on how to set up other supported notification services.

## Testing your notifications

You can use a simple script to test that your notifications are working:

```python
from loguru import logger

# This will send a notification if you've set notification_level to ERROR or lower
logger.error("Test notification - this is an error message")

# This will send a notification if you've set notification_level to CRITICAL
logger.critical("Test notification - this is a critical message")
```
