"""
Module for sending alerts to notification services.

This module provides functions for sending alerts to notification services
using the Apprise library.

License:
    MIT

"""

import apprise


class ManualSender(apprise.Apprise):
    """
    Class for sending alerts to notification services.

    This class extends the Apprise library to provide a simple interface for
    sending alerts to various notification services using Apprise URLs.

    """

    def __init__(self, urls: list[str]) -> None:
        """
        Manual sender.

        Args:
            urls: List of Apprise URLs for sending alerts through notification services.

        """
        super().__init__()
        self.add(urls)
