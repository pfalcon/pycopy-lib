# Should be reimplemented for Pycopy
# Reason:
# CPython implementation brings in metaclasses and other bloat.
# This is going to be just import-all for other modules in a namespace package
import ucollections
from ucollections import OrderedDict
try:
    from .defaultdict import defaultdict
except ImportError:
    pass
try:
    from .deque import deque
except ImportError:
    pass

class Mapping:
    pass

class MutableMapping:
    pass

def namedtuple(name, fields):
    _T = ucollections.namedtuple(name, fields)

    @classmethod
    def _make(cls, seq):
        return cls(*seq)

    t = type(name, (_T,), {"_make": _make})

    return t
