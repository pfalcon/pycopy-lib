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
    for i, props in {
        "md5": {"digest_size": 16, "block_size": 64},
        "sha1": {"digest_size": 20, "block_size": 64},
        "sha224": edict,
        "sha256": {"digest_size": 32, "block_size": 64},
        "sha384": edict,
        "sha512": edict
    }.items():
        c = getattr(uhashlib, i, None)
        if not c:
            try:
                c = __import__("_" + i, None, None, (), 1)
            except ImportError:
                continue
            c = getattr(c, i)
        else:
            c = type(i, (c, _hd_mixin), props)
        globals()[i] = c

init()


def new(algo, data=b""):
    try:
        c = globals()[algo]
        return c(data)
    except KeyError:
        raise ValueError(algo)
