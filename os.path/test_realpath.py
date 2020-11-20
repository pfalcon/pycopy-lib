from os.path import realpath


rp = realpath(__file__)
print(__file__)
print(rp)
assert rp.endswith("/os.path/test_realpath.py")
