"""
Tests for the kamihi.base.manual_send module.

License:
    MIT

"""
import os


def test_alert_manager_init_empty():
    """Test that AlertManager initializes correctly with no URLs."""
    from kamihi.base.manual_send import get_notifier
    notifier = get_notifier()
    assert len(notifier) == 0

def test_alert_manager_init_urls():
    """Test that AlertManager initializes correctly with URLs."""
    os.environ["KAMIHI_ALERT_URLS"] = '["discord://webhook_id/webhook_token", "mailto://domain.com?user=userid&pass=password"]'
    from kamihi.base.manual_send import get_notifier
    notifier = get_notifier()
    assert len(notifier) == 2
