"""
Pytest hooks.

License:
    MIT

"""

import pytest
from _pytest.nodes import Item
from _pytest.runner import CallInfo
from _pytest.terminal import TerminalReporter
from pluggy import Result
from telethon.errors import FloodWaitError

from tests.fixtures.docker_container import KamihiContainer
from tests.fixtures.settings import TestingSettings


def pytest_set_filtered_exceptions():
    """
    All tests will fail unless they raise one of the exceptions listed here.
    """
    return [FloodWaitError]


def pytest_xdist_auto_num_workers(config):
    """
    Automatically determine the number of workers for xdist based on credentials available.
    """
    setts = TestingSettings()

    return max(1, len(setts.credentials))


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item: Item):
    outcome = yield
    rep: Result = outcome.get_result()

    if rep.when == "call" and rep.failed:
        kamihi_container: KamihiContainer = item.funcargs.get("kamihi_container")
        if kamihi_container:
            logs = kamihi_container.get_text("/app/kamihi.log")["kamihi.log"]
            rep.sections.append(("Command logs", logs))


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    report_data = getattr(config, "_docker_cleanup_report", None)
    if report_data:
        terminalreporter.write_sep("-", "Docker cleanup report")
        terminalreporter.write_line(
            f"{len(report_data['containers']['ContainersDeleted'] or [])} containers removed ({report_data['containers']['SpaceReclaimed'] / 1024 / 1024:.2f} MB)"
        )
        terminalreporter.write_line(
            f"{len(report_data['volumes']['VolumesDeleted'] or [])} volumes removed ({report_data['volumes']['SpaceReclaimed'] / 1024 / 1024:.2f} MB)"
        )
        terminalreporter.write_line(
            f"{len(report_data['images']['ImagesDeleted'] or [])} images removed ({report_data['images']['SpaceReclaimed'] / 1024 / 1024:.2f} MB)"
        )
        terminalreporter.write_line("\n")
