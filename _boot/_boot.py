from sys import print_exception, stderr


def vars(obj):
    return {k: getattr(obj, k) for k in dir(obj) if not k.startswith("__")}


def _setup():
    import builtins

    builtins.vars = vars
    builtins.FileNotFoundError = OSError

    from micropython import writable_ns
    import string

    PATCHES = {
        str: (
            string, ("expandtabs", "isidentifier", "ljust", "translate"),
        ),
    }

    for typ, (mod, idlist) in PATCHES.items():
        writable_ns(typ, True)
        for name in idlist:
            setattr(typ, name, getattr(mod, name))
        writable_ns(typ, False)


try:
    _setup()
except Exception as e:
    print_exception(e, stderr)
    raise
