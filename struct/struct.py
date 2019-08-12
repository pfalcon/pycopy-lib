import sys
import ustruct


error = ValueError


def _norm_fmt(fmt):
    f = ""
    if fmt.startswith("="):
        f = "<"
        if sys.byteorder == "big":
            f = ">"
    elif fmt.startswith("!"):
        f = ">"
    if f:
        fmt = f + fmt[1:]

    fmt = fmt.replace("?", "B")
    # TODO: should check for count
    fmt = fmt.replace("c", "1s")
    # Assume that size_t matches long
    fmt = fmt.replace('n', 'l')
    fmt = fmt.replace('N', 'L')

    return fmt


def calcsize(fmt):
    return ustruct.calcsize(_norm_fmt(fmt))


def pack(fmt, *vals):
    return ustruct.pack(_norm_fmt(fmt), *vals)


def unpack(fmt, buf):
    return ustruct.unpack(_norm_fmt(fmt), buf)


class Struct:

    def __init__(self, format):
        self.format = format
        self.size = calcsize(format)

    def unpack(self, buf):
        return unpack(self.format, buf)

    def pack(self, *vals):
        return pack(self.format, *vals)
