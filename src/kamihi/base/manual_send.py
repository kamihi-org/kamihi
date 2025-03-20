"""
Module for sending alerts to notification services.

This module provides functions for sending alerts to notification services
using the Apprise library. The notification services are configured in the
settings module.

License:
    MIT

Examples:
    >>> from kamihi.base.manual_send import get_notifier
    >>> notifier = get_notifier()
    >>> notifier.notify(title="Test", body="This is a test message.")

"""

import apprise

from .config import get_settings

_settings = get_settings()
_notifier = apprise.Apprise()
_notifier.add(_settings.alert_urls)


def get_notifier() -> apprise.Apprise:
    """
    Get the current notifier.

    This function returns the current notifier object, which can be used
    to send alerts through notification services.

    Returns:
        apprise.Apprise: The current notifier object.

    """
    return _notifier
