"""
Tests for the kamihi.base.config module.

License:
    MIT

"""

from kamihi.base.config import KamihiSettings, get_settings


def test_default_settings():
    """Test that the default settings are loaded correctly."""
    # Get the settings
    settings = get_settings()

    # Check the configuration settings
    assert settings.model_config["env_prefix"] == "KAMIHI_"
    assert settings.model_config["env_file"] == ".env"
    assert settings.model_config["env_file_encoding"] == "utf-8"
    assert settings.model_config["case_sensitive"] == False
    assert settings.model_config["extra"] == "ignore"
