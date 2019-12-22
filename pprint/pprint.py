import sys
import uio


def pformat(obj, indent=1, width=80, depth=None):
    buf = uio.StringIO()
    _pprint(obj, buf, indent, width, depth)
    return buf.getvalue()


def _pprint(obj, stream=None, indent=1, width=80, depth=None):
    if stream is None:
        stream = sys.stdout

    if isinstance(obj, dict):
        stream.write("{\n")
        for k, v in obj.items():
            stream.write("  ")
            _pprint(k, stream, indent, width, depth)
            stream.write(": ")
            _pprint(v, stream, indent, width, depth)
            stream.write(",\n")
        stream.write("}")
    else:
        print(repr(obj), file=stream, end="")


def pprint(obj, stream=None, indent=1, width=80, depth=None):
    _pprint(obj, stream, indent, width, depth)
    print(file=stream)
