import os


f = os.popen("echo $_PYCOPY_LIB_TESTVAR2")
s = f.read()
assert(s == "\n")
os.environ["_PYCOPY_LIB_TESTVAR2"] = "12345"
f = os.popen("echo $_PYCOPY_LIB_TESTVAR2")
s = f.read()
print(repr(s))
assert s == "12345\n"
