import sys


def warn(msg, cat=None, stacklevel=1):
    print("%s: %s" % ("Warning" if cat is None else cat.__name__, msg), file=sys.stderr)
