import ubinascii
try:
    import uhashlib
except ImportError:
    uhashlib = None


class _hd_mixin:

    def hexdigest(self):
        s = ubinascii.hexlify(self.digest())
        s.__class__ = str
        return s


def init():
    edict = {}
    for i in ("md5", "sha1", "sha224", "sha256", "sha384", "sha512"):
        c = getattr(uhashlib, i, None)
        if not c:
            try:
                c = __import__("_" + i, None, None, (), 1)
            except ImportError:
                continue
            c = getattr(c, i)
        else:
            c = type(i, (c, _hd_mixin), edict)
        globals()[i] = c

init()


def new(algo, data=b""):
    try:
        c = globals()[algo]
        return c(data)
    except KeyError:
        raise ValueError(algo)
