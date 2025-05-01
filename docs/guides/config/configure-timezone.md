The default timezone for the server is UTC. You can change the timezone by setting the `TZ` environment variable in your `.env` file. For example, to set the timezone to `America/New_York`, you would add the following line to your `.env` file:

=== "Config. file"
    ```yaml
    timezone: America/New_York
    ```
=== "`.env` file"
    ```bash
    KAMIHI_TIMEZONE=America/New_York
    ```
=== "Programmatically"
    ```python
    from kamihi import bot
    
    bot.settings.timezone = "America/New_York"
    ```

You can get the list of available timezones from [here](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).
