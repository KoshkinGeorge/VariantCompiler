import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--runmanual", action="store_true", default=False, help="run manual tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "marks tests which require manual checking")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runmanual"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_manual = pytest.mark.skip(reason="need --runmanual option to run")
    for item in items:
        if "manual" in item.keywords:
            item.add_marker(skip_manual)