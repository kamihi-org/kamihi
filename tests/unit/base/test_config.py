"""
Tests for the kamihi.base.config module.

License:
    MIT

"""

import os
import tempfile
from unittest.mock import patch

import pytest
import pytz
from pydantic import ValidationError

from kamihi.base.config import KamihiSettings, LogSettings


def test_env_var_overrides_default():
    """Test that environment variables override default values."""
    # Default is INFO
    default_settings = KamihiSettings()
    assert default_settings.log.stdout_level == "INFO"

    # Override with env var
    with patch.dict(os.environ, {"KAMIHI_LOG__STDOUT_LEVEL": "WARNING"}):
        settings = KamihiSettings()
        assert settings.log.stdout_level == "WARNING"


def test_config_file_loading():
    """Test that configuration is correctly loaded from a file."""
    # Create a temporary YAML config file
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+", delete=False) as temp_file:
        temp_file.write("""
log:
  stdout_level: WARNING
  stderr_enable: true
        """)
        config_path = temp_file.name

    try:
        # Set environment variable to point to our config file
        with patch.dict(os.environ, {"KAMIHI_CONFIG_FILE": config_path}):
            # Load settings
            settings = KamihiSettings()

            # Verify config file values were loaded
            assert settings.log.stdout_level == "WARNING"  # Changed from default
            assert settings.log.stderr_enable is True  # Changed from default
    finally:
        # Clean up
        if os.path.exists(config_path):
            os.unlink(config_path)


def test_parameters_have_valid_values():
    """Test that validation catches invalid parameter values."""
    # Test with an invalid log level (must match pattern)
    with patch.dict(os.environ, {"KAMIHI_LOG__STDOUT_LEVEL": "INVALID_LEVEL"}), pytest.raises(ValidationError):
        KamihiSettings()


def test_parameters_have_correct_types():
    """Test that validation catches incorrect parameter types."""
    # Test with a boolean field given a non-boolean value
    with patch.dict(os.environ, {"KAMIHI_LOG__STDOUT_ENABLE": "not_a_boolean"}), pytest.raises(ValidationError):
        KamihiSettings()


def test_config_custom_location_via_env():
    """Test loading configuration from a custom location specified by env var."""
    # Create a temporary YAML config file
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+", delete=False) as temp_file:
        temp_file.write("""
log:
  stdout_level: DEBUG
        """)
        config_path = temp_file.name

    try:
        # Set environment variable to point to our config file
        with patch.dict(os.environ, {"KAMIHI_CONFIG_FILE": config_path}):
            # Load settings
            settings = KamihiSettings()

            # Verify config was loaded from custom location
            assert settings.log.stdout_level == "DEBUG"
    finally:
        # Clean up
        if os.path.exists(config_path):
            os.unlink(config_path)


def test_config_location_fallback():
    """Test fallback to default location when custom location is invalid."""
    # Set environment variable to nonexistent file
    with patch.dict(
        os.environ,
        {
            "KAMIHI_CONFIG_FILE": "/nonexistent/file.yaml",
            "KAMIHI_LOG__STDOUT_LEVEL": "ERROR",  # This should still be applied
        },
    ):
        # Load settings
        settings = KamihiSettings()

        # Even though YAML file wasn't found, env vars should still work
        assert settings.log.stdout_level == "ERROR"
        # And defaults for other fields should be preserved
        assert settings.log.stdout_enable is True


def test_config_location_preference_order():
    """Test order of preference between different configuration locations."""
    # Create a YAML file with one set of values
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+", delete=False) as temp_file:
        temp_file.write("""
log:
  stdout_level: WARNING
  stderr_level: ERROR
        """)
        config_path = temp_file.name

    try:
        # Set up environment with config file path and override one value
        with patch.dict(
            os.environ,
            {
                "KAMIHI_CONFIG_FILE": config_path,
                "KAMIHI_LOG__STDOUT_LEVEL": "DEBUG",  # Should override YAML file
            },
        ):
            # Load settings
            settings = KamihiSettings()

            # Environment variable should take precedence over YAML
            assert settings.log.stdout_level == "DEBUG"
            # But YAML should still apply for other fields
            assert settings.log.stderr_level == "ERROR"
    finally:
        # Clean up
        if os.path.exists(config_path):
            os.unlink(config_path)


def test_config_reload_on_location_change():
    """Test configuration reload when location changes."""
    # Create first config file
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+", delete=False) as file1:
        file1.write("""
log:
  stdout_level: WARNING
        """)
        path1 = file1.name

    # Create second config file
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+", delete=False) as file2:
        file2.write("""
log:
  stdout_level: DEBUG
        """)
        path2 = file2.name

    try:
        # First load with first config
        with patch.dict(os.environ, {"KAMIHI_CONFIG_FILE": path1}):
            settings1 = KamihiSettings()
            assert settings1.log.stdout_level == "WARNING"

        # Then load with second config
        with patch.dict(os.environ, {"KAMIHI_CONFIG_FILE": path2}):
            settings2 = KamihiSettings()
            # Should load from new location
            assert settings2.log.stdout_level == "DEBUG"
    finally:
        # Clean up
        for path in [path1, path2]:
            if os.path.exists(path):
                os.unlink(path)


def test_config_file_overrides_default():
    """Test that config file values override default values."""
    # Create a config file with non-default values
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+", delete=False) as temp_file:
        temp_file.write("""
log:
  stdout_level: WARNING
        """)
        config_path = temp_file.name

    try:
        # Load with config file
        with patch.dict(os.environ, {"KAMIHI_CONFIG_FILE": config_path}):
            settings = KamihiSettings()
            # Config file should override default
            assert settings.log.stdout_level == "WARNING"  # Default is INFO
    finally:
        # Clean up
        if os.path.exists(config_path):
            os.unlink(config_path)


def test_env_var_overrides_config_file():
    """Test that environment variables override config file values."""
    # Create a config file with some values
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+", delete=False) as temp_file:
        temp_file.write("""
log:
  stdout_level: WARNING
        """)
        config_path = temp_file.name

    try:
        # Set environment with both config file and override env var
        with patch.dict(
            os.environ,
            {
                "KAMIHI_CONFIG_FILE": config_path,
                "KAMIHI_LOG__STDOUT_LEVEL": "ERROR",  # Should override YAML
            },
        ):
            settings = KamihiSettings()
            # Env var should override config file
            assert settings.log.stdout_level == "ERROR"
    finally:
        # Clean up
        if os.path.exists(config_path):
            os.unlink(config_path)


def test_full_precedence_chain():
    """Test complete precedence chain for configuration sources."""
    # Create a config file
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+", delete=False) as temp_file:
        temp_file.write("""
log:
  stdout_level: WARNING
        """)
        config_path = temp_file.name

    try:
        # Set up environment with multiple configuration sources:
        # 1. Default value (INFO from code)
        # 2. YAML file value (WARNING)
        # 3. Env var value (ERROR)
        with patch.dict(os.environ, {"KAMIHI_CONFIG_FILE": config_path, "KAMIHI_LOG__STDOUT_LEVEL": "ERROR"}):
            settings = KamihiSettings()

            # Env var should have the highest precedence
            assert settings.log.stdout_level == "ERROR"

            # Create a new settings object with direct initialization overrides
            # (simulating programmatic override, highest precedence)
            override_settings = KamihiSettings(log=LogSettings(stdout_level="CRITICAL"))
            assert override_settings.log.stdout_level == "CRITICAL"
    finally:
        # Clean up
        if os.path.exists(config_path):
            os.unlink(config_path)


@pytest.mark.parametrize(
    "timezone",
    [
        "UTC",
        "America/New_York",
        "Europe/London",
        "Asia/Tokyo",
        "Australia/Sydney",
        "America/Los_Angeles",
        "Europe/Berlin",
        "America/Chicago",
        "Asia/Kolkata",
        "Africa/Cairo",
    ],
)
def test_timezone_validation_valid(timezone):
    """Test that valid timezones are accepted."""
    # Test with a valid timezone
    with patch.dict(os.environ, {"KAMIHI_TIMEZONE": timezone}):
        settings = KamihiSettings()
        assert settings.timezone == timezone


def test_timezone_validation_invalid():
    """Test that invalid timezones raise a validation error."""
    # Test with an invalid timezone
    with patch.dict(os.environ, {"KAMIHI_TIMEZONE": "AAA/AAA"}), pytest.raises(ValidationError):
        KamihiSettings()


def test_timezone_obj_property():
    """Test that the timezone_obj property returns the correct timezone object."""
    # Test with a specific timezone
    with patch.dict(os.environ, {"KAMIHI_TIMEZONE": "Asia/Tokyo"}):
        settings = KamihiSettings()
        # Check that it's the correct type
        assert isinstance(settings.timezone_obj, pytz.tzinfo.DstTzInfo)
        # Check that it's the correct timezone
        assert settings.timezone_obj == pytz.timezone("Asia/Tokyo")

    # Test with UTC (default)
    settings = KamihiSettings()
    assert settings.timezone == "UTC"
    assert settings.timezone_obj == pytz.timezone("UTC")


@pytest.mark.parametrize(
    "host",
    [
        "mongodb://localhost",
        "mongodb://localhost:27017",
        "mongodb+srv://cluster0.mongodb.net",
        "mongodb://user:password@localhost:27017",
        "mongodb://user:password@localhost:27017",
    ],
)
def test_db_host(host: str):
    """Test that the database host is set correctly."""
    # Test with a specific host
    with patch.dict(os.environ, {"KAMIHI_DB__HOST": host}):
        settings = KamihiSettings()
        assert settings.db.host == host
