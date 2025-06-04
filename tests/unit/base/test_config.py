"""
Tests for the kamihi.base.config module.

License:
    MIT

"""

import os
import tempfile
from pathlib import Path
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


def test_from_yaml_with_valid_file():
    """Test loading settings from a valid YAML file."""
    # Create a temporary YAML file with valid configuration
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+", delete=False) as temp_file:
        temp_file.write("""
log:
  stdout_level: WARNING
  stderr_enable: true
  file_enable: true
  file_path: custom.log
db:
  host: mongodb://testhost:27017
  name: testdb
timezone: Europe/London
        """)
        yaml_path = Path(temp_file.name)

    try:
        # Load settings from YAML file
        settings = KamihiSettings.from_yaml(yaml_path)

        # Verify all settings were loaded correctly
        assert settings.log.stdout_level == "WARNING"
        assert settings.log.stderr_enable is True
        assert settings.log.file_enable is True
        assert settings.log.file_path == "custom.log"
        assert settings.db.host == "mongodb://testhost:27017"
        assert settings.db.name == "testdb"
        assert settings.timezone == "Europe/London"
    finally:
        # Clean up
        if yaml_path.exists():
            yaml_path.unlink()


def test_from_yaml_with_partial_config():
    """Test loading settings from a YAML file with only partial configuration."""
    # Create a temporary YAML file with partial configuration
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+", delete=False) as temp_file:
        temp_file.write("""
log:
  stdout_level: ERROR
timezone: Asia/Tokyo
        """)
        yaml_path = Path(temp_file.name)

    try:
        # Load settings from YAML file
        settings = KamihiSettings.from_yaml(yaml_path)

        # Verify specified settings were loaded
        assert settings.log.stdout_level == "ERROR"
        assert settings.timezone == "Asia/Tokyo"

        # Verify default values are preserved for unspecified settings
        assert settings.log.stderr_enable is False  # Default value
        assert settings.db.host == "mongodb://localhost:27017"  # Default value
        assert settings.testing is False  # Default value
    finally:
        # Clean up
        if yaml_path.exists():
            yaml_path.unlink()


def test_from_yaml_with_nonexistent_file():
    """Test loading settings from a non-existent YAML file returns default settings."""
    # Use a path that doesn't exist
    nonexistent_path = Path("/tmp/nonexistent_config.yaml")

    # Ensure the file doesn't exist
    assert not nonexistent_path.exists()

    # Load settings from non-existent file
    settings = KamihiSettings.from_yaml(nonexistent_path)

    # Verify default settings are returned
    assert settings.log.stdout_level == "INFO"  # Default value
    assert settings.log.stderr_enable is False  # Default value
    assert settings.db.host == "mongodb://localhost:27017"  # Default value
    assert settings.timezone == "UTC"  # Default value
    assert settings.testing is False  # Default value


def test_from_yaml_with_empty_file():
    """Test loading settings from an empty YAML file returns default settings."""
    # Create an empty YAML file
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+", delete=False) as temp_file:
        temp_file.write("")  # Empty file
        yaml_path = Path(temp_file.name)

    try:
        # Load settings from empty file
        settings = KamihiSettings.from_yaml(yaml_path)

        # Verify default settings are returned
        assert settings.log.stdout_level == "INFO"  # Default value
        assert settings.log.stderr_enable is False  # Default value
        assert settings.db.host == "mongodb://localhost:27017"  # Default value
        assert settings.timezone == "UTC"  # Default value
        assert settings.testing is False  # Default value
    finally:
        # Clean up
        if yaml_path.exists():
            yaml_path.unlink()


def test_from_yaml_with_null_content():
    """Test loading settings from a YAML file with null content returns default settings."""
    # Create a YAML file with null content
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+", delete=False) as temp_file:
        temp_file.write("~")  # YAML null
        yaml_path = Path(temp_file.name)

    try:
        # Load settings from file with null content
        settings = KamihiSettings.from_yaml(yaml_path)

        # Verify default settings are returned
        assert settings.log.stdout_level == "INFO"  # Default value
        assert settings.log.stderr_enable is False  # Default value
        assert settings.db.host == "mongodb://localhost:27017"  # Default value
        assert settings.timezone == "UTC"  # Default value
        assert settings.testing is False  # Default value
    finally:
        # Clean up
        if yaml_path.exists():
            yaml_path.unlink()


def test_from_yaml_with_invalid_yaml():
    """Test loading settings from a YAML file with invalid YAML syntax raises an error."""
    # Create a YAML file with invalid syntax
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+", delete=False) as temp_file:
        temp_file.write("""
log:
  stdout_level: WARNING
    invalid_indentation: true
        """)
        yaml_path = Path(temp_file.name)

    try:
        # Loading from invalid YAML should raise an exception
        with pytest.raises(Exception):
            KamihiSettings.from_yaml(yaml_path)
    finally:
        # Clean up
        if yaml_path.exists():
            yaml_path.unlink()


def test_from_yaml_with_invalid_config_values():
    """Test loading settings from a YAML file with invalid configuration values raises validation error."""
    # Create a YAML file with invalid configuration values
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+", delete=False) as temp_file:
        temp_file.write("""
log:
  stdout_level: INVALID_LEVEL
timezone: Invalid/Timezone
        """)
        yaml_path = Path(temp_file.name)

    try:
        # Loading with invalid values should raise ValidationError
        with pytest.raises(ValidationError):
            KamihiSettings.from_yaml(yaml_path)
    finally:
        # Clean up
        if yaml_path.exists():
            yaml_path.unlink()


def test_from_yaml_with_directory_path():
    """Test loading settings from a directory path returns default settings."""
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        dir_path = Path(temp_dir)

        # Ensure it's a directory, not a file
        assert dir_path.is_dir()

        # Load settings from directory path
        settings = KamihiSettings.from_yaml(dir_path)

        # Verify default settings are returned
        assert settings.log.stdout_level == "INFO"  # Default value
        assert settings.log.stderr_enable is False  # Default value
        assert settings.db.host == "mongodb://localhost:27017"  # Default value
        assert settings.timezone == "UTC"  # Default value
        assert settings.testing is False  # Default value


def test_from_yaml_with_complex_nested_config():
    """Test loading settings from a YAML file with complex nested configuration."""
    # Create a temporary YAML file with complex nested configuration
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+", delete=False) as temp_file:
        temp_file.write("""
log:
  stdout_enable: true
  stdout_level: DEBUG
  stdout_serialize: true
  stderr_enable: true
  stderr_level: CRITICAL
  stderr_serialize: false
  file_enable: true
  file_level: WARNING
  file_path: /var/log/kamihi.log
  file_serialize: true
  file_rotation: 10 MB
  file_retention: 30 days
  notification_enable: true
  notification_level: SUCCESS
  notification_urls:
    - https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX
    - https://discord.com/api/webhooks/123456789/abcdefgh
db:
  host: mongodb+srv://user:password@cluster0.mongodb.net
  name: production_db
responses:
  default_enabled: false
  default_message: Custom default message
  error_message: Custom error message
web:
  host: 0.0.0.0
  port: 8080
timezone: America/New_York
testing: false
autoreload_templates: false
        """)
        yaml_path = Path(temp_file.name)

    try:
        # Load settings from YAML file
        settings = KamihiSettings.from_yaml(yaml_path)

        # Verify all log settings
        assert settings.log.stdout_enable is True
        assert settings.log.stdout_level == "DEBUG"
        assert settings.log.stdout_serialize is True
        assert settings.log.stderr_enable is True
        assert settings.log.stderr_level == "CRITICAL"
        assert settings.log.stderr_serialize is False
        assert settings.log.file_enable is True
        assert settings.log.file_level == "WARNING"
        assert settings.log.file_path == "/var/log/kamihi.log"
        assert settings.log.file_serialize is True
        assert settings.log.file_rotation == "10 MB"
        assert settings.log.file_retention == "30 days"
        assert settings.log.notification_enable is True
        assert settings.log.notification_level == "SUCCESS"
        assert settings.log.notification_urls == [
            "https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX",
            "https://discord.com/api/webhooks/123456789/abcdefgh",
        ]

        # Verify database settings
        assert settings.db.host == "mongodb+srv://user:password@cluster0.mongodb.net"
        assert settings.db.name == "production_db"

        # Verify response settings
        assert settings.responses.default_enabled is False
        assert settings.responses.default_message == "Custom default message"
        assert settings.responses.error_message == "Custom error message"

        # Verify web settings
        assert settings.web.host == "0.0.0.0"
        assert settings.web.port == 8080

        # Verify general settings
        assert settings.timezone == "America/New_York"
        assert settings.testing is False
        assert settings.autoreload_templates is False
    finally:
        # Clean up
        if yaml_path.exists():
            yaml_path.unlink()


def test_from_yaml_preserves_defaults_for_missing_sections():
    """Test that missing sections in YAML preserve their default values."""
    # Create a YAML file with only one section
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+", delete=False) as temp_file:
        temp_file.write("""
timezone: Europe/Paris
        """)
        yaml_path = Path(temp_file.name)

    try:
        # Load settings from YAML file
        settings = KamihiSettings.from_yaml(yaml_path)

        # Verify specified setting
        assert settings.timezone == "Europe/Paris"

        # Verify all other sections preserve defaults
        assert settings.log.stdout_level == "INFO"  # Default LogSettings
        assert settings.log.stderr_enable is False  # Default LogSettings
        assert settings.db.host == "mongodb://localhost:27017"  # Default DatabaseSettings
        assert settings.db.name == "kamihi"  # Default DatabaseSettings
        assert settings.responses.default_enabled is True  # Default ResponseSettings
        assert settings.web.host == "localhost"  # Default WebSettings
        assert settings.web.port == 4242  # Default WebSettings
        assert settings.testing is False  # Default value
        assert settings.autoreload_templates is True  # Default value
    finally:
        # Clean up
        if yaml_path.exists():
            yaml_path.unlink()
