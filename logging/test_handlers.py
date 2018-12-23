# Note: this test is not compliant with CPython's logging module
import os
import logging
from logging.handlers import RotatingFileHandler


class DummyStream:
    def __init__(self):
        self._data = ""

    def write(self, s):
        self._data += s

    def close(self):
        pass

fmt = logging.Formatter("%(levelname)s:%(name)s: %(message)s")

# StreamHandler
logger = logging.getLogger("testlogger")
strm = DummyStream()
sh = logging.StreamHandler(strm)
sh.setFormatter(fmt)
logger.addHandler(sh)

# FileHandler
try:
    os.remove("fh.log")
except OSError:
    pass

fh_fname = "fh.log"
fh = logging.FileHandler(fh_fname)
fh.setFormatter(fmt)
logger.addHandler(fh)

# RotatingFileHandler
rfh = RotatingFileHandler("rfh.log", maxBytes=20, backupCount=3)
rfh.setFormatter(fmt)
logger.addHandler(rfh)

for i in range(3, -1, -1):
    logger.warning("x%i", i)

# this should be the logging result
res = "\n".join(
    ("WARNING:testlogger: x{0}".format(i) for i in range(3, -1, -1))
) + "\n"

# check StreamHandler output
assert strm._data == res, "%r vs %r" % (strm._data, res)

# check FileHandler
with open(fh_fname) as f:
    assert f.read() == res

# check RotatingFileHandler output
with open("rfh.log") as f:
    assert f.read() == "WARNING:testlogger: x0\n"

for i in range(1, 4):
    fn = "rfh.log.%i" % i
    with open(fn) as f:
        assert f.read() == "WARNING:testlogger: x%i\n" % i

for fn in ["rfh.log"] + ["rfh.log.{0}".format(i) for i in range(1, 4)]:
    os.remove(fn)
os.remove("fh.log")
