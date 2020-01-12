from sys import print_exception, stderr


def vars(obj):
    return {k: getattr(obj, k) for k in dir(obj) if not k.startswith("__")}


def _setup():
    import builtins

    builtins.vars = vars
    builtins.FileNotFoundError = OSError


try:
    _setup()
except Exception as e:
    print_exception(e, stderr)
    raise
