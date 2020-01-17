import zlib


DATA = b"foo"

cdata = zlib.compress(DATA)
#print(cdata)
assert cdata != DATA
assert zlib.decompress(cdata) == DATA
