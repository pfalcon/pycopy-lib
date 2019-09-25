import uio


def pformat(obj, indent=1, width=80, depth=None):
    buf = uio.StringIO()
    pprint(obj, buf, indent, width, depth)
    return buf.getvalue()


def pprint(obj, stream=None, indent=1, width=80, depth=None):
    print(repr(obj), file=stream)
