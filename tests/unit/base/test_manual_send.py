"""
Tests for the kamihi.base.manual_send module.

License:
    MIT

"""

from unittest.mock import patch

from kamihi.base.manual_send import ManualSender


def test_initialization_with_single_url():
    # Test with a single URL
    urls = ["mailto://user:password@example.com"]
    sender = ManualSender(urls)

    # Verify the URL was added
    assert len(sender) == 1


def test_initialization_with_multiple_urls():
    # Test with multiple URLs
    urls = [
        "mailto://user:password@example.com",
        "discord://webhook_id/webhook_token",
    ]
    sender = ManualSender(urls)

    # Verify all URLs were added
    assert len(sender) == 2


def test_initialization_with_empty_url_list():
    # Test with an empty list
    urls = []
    sender = ManualSender(urls)

    # Verify no servers were added
    assert len(sender) == 0


@patch("apprise.Apprise.notify")
def test_send_notification(mock_notify):
    # Setup
    mock_notify.return_value = True
    urls = ["mailto://user:password@example.com"]
    sender = ManualSender(urls)

    # Test sending a notification
    result = sender.notify(body="Test message", title="Test title")

    # Verify the notification was sent
    assert result is True
    mock_notify.assert_called_once_with(body="Test message", title="Test title")


@patch("apprise.Apprise.add")
def test_add_method_called_with_urls(mock_add):
    # Test that the constructor passes URLs to add
    urls = ["mailto://user:password@example.com"]
    ManualSender(urls)

    # Verify add was called with the correct URLs
    mock_add.assert_called_once_with(urls)


def test_initialization_with_invalid_url():
    # Test that invalid URLs are handled appropriately
    urls = ["invalid://url"]
    sender = ManualSender(urls)

    # An invalid URL might still be added to servers but won't be saved
    # This test ensures the constructor doesn't raise exceptions with invalid URLs
    assert len(sender) == 0
