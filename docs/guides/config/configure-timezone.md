The default timezone for the bot is UTC. You can change it by adjusting the `settings.timezone` variable:

=== "`kamihi.yml`"
    ```yaml
    timezone: America/New_York
    ```
=== "`.env`"
    ```bash
    KAMIHI_TIMEZONE=America/New_York
    ```
=== "Programmatically"
    ```python
    from kamihi import bot
    
    bot.settings.timezone = "America/New_York"
    ```

You can get the list of available timezones from [here](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones).
