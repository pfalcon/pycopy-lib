# Helper module to load compiled bytecode files, for both MicroPython and
# CPython
import sys


if sys.implementation.name == "micropython":
    import mpylib

    def loadbc(f):
        mpy = mpylib.MPYInput(f)
        mpy.read_header()
        codeobj = mpy.read_raw_code()
        return codeobj
else:
    import marshal

    # Older versions (Python2) lacked src_size.
    # ref: importlib._bootstrap, search for "marshal"
    def loadbc(f):
        magic = f.read(4)
        src_mtime = f.read(4)
        src_size = f.read(4)
        codeobj = marshal.load(f)
        return codeobj
