#!/usr/bin/env python3
import os
import sys
from pyqode.core import widgets
from gnucobolide import backend


class GenericCodeEdit(widgets.GenericCodeEdit):
    """
    This editor is used for non COBOL documents.
    """
    def __init__(self, parent=None):
        cwd = os.path.dirname(sys.executable)
        base_backend = 'core-backend'
        if sys.platform == 'win32':
            base_backend += '.exe'
        super().__init__(
            parent, server_script=os.path.join(cwd, base_backend)
            if hasattr(sys, 'frozen') else backend.__file__)
