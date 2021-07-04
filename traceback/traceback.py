import sys

def format_tb(tb, limit):
    return ["traceback.format_tb() not implemented\n"]

def format_exception_only(etype, value):
    s = str(value)
    t = type(value).__name__
    if s:
        return ["%s: %s\n" % (t, s)]
    else:
        return ["%s\n" % t]

def format_exception(etype, value, tb, limit=None, chain=True):
    return format_exception_only(etype, value)

def print_exception(t, e, tb, limit=None, file=None, chain=True):
    if file is None:
        file = sys.stdout
    sys.print_exception(e, file)

def print_exc(limit=None, file=None, chain=True):
    print_exception(*sys.exc_info(), limit=limit, file=file, chain=chain)

def format_exc(limit=None, chain=True):
    return "".join(format_exception(*sys.exc_info(), limit=limit, chain=chain))
