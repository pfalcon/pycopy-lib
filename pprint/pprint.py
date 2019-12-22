import sys
import uio


def pformat(obj, indent=1, width=80, depth=None):
    buf = uio.StringIO()
    pprint(obj, buf, indent, width, depth)
    return buf.getvalue()


def pprint(obj, stream=None, indent=1, width=80, depth=None):
    if stream is None:
        stream = sys.stdout

    if isinstance(obj, dict):
        stream.write("{\n")
        for k, v in obj.items():
            stream.write("  ")
            pprint(k, stream, indent, width, depth)
            stream.write(": ")
            pprint(v, stream, indent, width, depth)
            stream.write(",\n")
        stream.write("}")
    else:
        print(repr(obj), file=stream, end="")

#    print(file=stream)
