from sys import print_exception, stderr


def vars(obj):
    return {k: getattr(obj, k) for k in dir(obj) if not k.startswith("__")}


def getrecursionlimit():
    return 100

class Warning(Exception):
    pass
class RuntimeWarning(Warning):
    pass


def _setup():
    import builtins

    builtins.vars = vars
    builtins.FileNotFoundError = OSError
    builtins.IOError = OSError
    builtins.Warning = Warning
    builtins.RuntimeWarning = RuntimeWarning

    from micropython import writable_ns
    import sys
    import string
    import byteslib
    import setlib

    PATCHES = {
        str: (
            string, ("capitalize", "encode", "expandtabs", "isalnum", "isidentifier", "ljust", "translate"),
        ),
        bytes: (
            byteslib, ("decode", "fromhex", "hex"),
        ),
        set: (
            setlib, ("update", "union", "intersection_update", "intersection", "difference_update", "difference"),
        ),
    }

    for typ, (mod, idlist) in PATCHES.items():
        writable_ns(typ, True)
        for name in idlist:
            setattr(typ, name, getattr(mod, name))
        writable_ns(typ, False)

    # sys is a special case which cannot be handled with wrapper module and
    # sys.modules["sys"] substitution, due to special handling of assignments
    # to sys.stdout and friends. So, patch the module namespace directly.
    writable_ns(sys, True)
    sys.getrecursionlimit = getrecursionlimit
    sys.executable = "pycopy-dev"
    sys.warnoptions = []
    writable_ns(sys, False)


try:
    _setup()
except Exception as e:
    print_exception(e, stderr)
    raise
