import hashlib

hs = hashlib.md5(b"foo")
assert hs.hexdigest() == "acbd18db4cc2f85cedef654fccc4a4d8"

hs = hashlib.sha1(b"foo")
hs.hexdigest() == "0beec7b5ea3f0fdbc95d0dd47f3c5bc275da8a33"

hs = hashlib.sha256(b"foo")
assert hs.hexdigest() == "2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae"
