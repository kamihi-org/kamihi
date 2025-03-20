"""
Tests for the kamihi.base.config module.

License:
    MIT

"""

import os
from kamihi.base.config import KamihiSettings, get_settings


def test_default_settings():
    """Test that the default settings are loaded correctly."""
    # Get the settings
    settings = get_settings()

    # Check the default values
    assert settings.alert_urls == []

    # Check the configuration settings
    assert settings.model_config["env_prefix"] == "KAMIHI_"
    assert settings.model_config["env_file"] == ".env"
    assert settings.model_config["env_file_encoding"] == "utf-8"
    assert settings.model_config["case_sensitive"] == False
    assert settings.model_config["extra"] == "ignore"

def test_env_settings():
    """Test that settings from environment variables are loaded correctly."""
    # Set the environment variables
    os.environ["KAMIHI_ALERT_URLS"] = '["telegram://123:abc@telegram","discord://webhook_id/webhook_token"]'

    # Reload settings
    settings = KamihiSettings()

    # Check the values
    assert "telegram://123:abc@telegram" in settings.alert_urls
    assert "discord://webhook_id/webhook_token" in settings.alert_urls

    # Clean up
    del os.environ["KAMIHI_ALERT_URLS"]
