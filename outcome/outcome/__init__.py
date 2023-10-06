# coding: utf-8
"""Top-level package for outcome."""

import sys

from ._util import AlreadyUsedError
from ._version import __version__

if sys.version_info >= (3, 5):
    from ._async import Error, Outcome, Value, acapture, capture
    __all__ = (
        'Error', 'Outcome', 'Value', 'acapture', 'capture', 'AlreadyUsedError'
    )
else:
    from ._sync import Error, Outcome, Value, capture
    __all__ = ('Error', 'Outcome', 'Value', 'capture', 'AlreadyUsedError')

