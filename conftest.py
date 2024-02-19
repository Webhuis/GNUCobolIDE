#!/usr/bin/env python3
"""
Configures the test suite and describe the global fixture that can be used
in functional tests.

"""
import pytest
import shutil
from gnucobolide import __version__, main
main.override_sys_path()
from gnucobolide.app import Application  # noqa
from gnucobolide.logger import setup_logging  # noqa
from gnucobolide.settings import Settings  # noqa

setup_logging(__version__)

_app = None


try:
    shutil.rmtree('test/testfiles/bin')
except OSError:
    pass


@pytest.fixture(scope="session")
def app(request):
    global _app
    # always starts with default settings
    s = Settings()
    s.clear()
    s.perspective = 'default'
    _app = Application(parse_args=False)

    def fin():
        global _app
        _app.exit()
        del _app

    # _app.win.hide()
    request.addfinalizer(fin)
    return _app
