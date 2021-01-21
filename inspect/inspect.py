import sys


def getmembers(obj, pred=None):
    res = []
    for name in dir(obj):
        val = getattr(obj, name)
        if pred is None or pred(val):
            res.append((name, val))
    res.sort()
    return res

def isfunction(obj):
    return isinstance(obj, type(isfunction))

def isgeneratorfunction(obj):
    return isinstance(obj, type(lambda:(yield)))

def isgenerator(obj):
    return isinstance(obj, type(lambda:(yield)()))

class _Class:
    def meth(): pass
_Instance = _Class()

def ismethod(obj):
    return isinstance(obj, type(_Instance.meth))

def isroutine(obj):
    return isfunction(obj) or ismethod(obj)

def isclass(obj):
    return isinstance(obj, type)

def ismodule(obj):
    return isinstance(obj, type(sys))

def iscode(obj):
    return False

def isframe(obj):
    return False

def istraceback(obj):
    return False


def getargspec(func):
    raise NotImplementedError("This is over-dynamic function, not supported by Pycopy")

def getmodule(obj, _filename=None):
    if ismodule(obj):
        return obj
    m = getattr(obj, "__module__", None)
    if m is not None:
        return sys.modules[m]
    print("Warning: inspect.getmodule(%r): returning None" % obj, file=sys.stderr)
    return None  # Not known

def getmro(cls):
    return [cls]

def getsourcefile(obj):
    return None  # Not known

def getfile(obj):
    return "<unknown>"

def getsource(obj):
    return "<source redacted to save you memory>"


def currentframe():
    return None

def getframeinfo(frame, context=1):
    return ("<unknown>", -1, "<unknown>", [""], 0)


def unwrap(func, *, stop=None):
    return func
