# Reimplement, because CPython3.3 impl is rather bloated
import os


def rmtree(top):
    for path, dirs, files in os.walk(top, False):
        for f in files:
            os.unlink(path + "/" + f)
        os.rmdir(path)

def copyfileobj(src, dest, length=512):
    if hasattr(src, "readinto"):
        buf = bytearray(length)
        while True:
            sz = src.readinto(buf)
            if not sz:
                break
            if sz == length:
                dest.write(buf)
            else:
                b = memoryview(buf)[:sz]
                dest.write(b)
    else:
        while True:
            buf = src.read(length)
            if not buf:
                break
            dest.write(buf)


def copyfile(src, dst, follow_symlinks=True):
    assert follow_symlinks
    with open(src, "rb") as srcf, open(dst, "wb") as dstf:
        copyfileobj(srcf, dstf)
