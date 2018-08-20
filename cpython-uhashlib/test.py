import hashlib
import uhashlib


md5 = hashlib.md5(b"foo")
umd5 = uhashlib.md5(b"foo")
md5.update(b"bar")
umd5.update(b"bar")
assert md5.digest() == umd5.digest()
