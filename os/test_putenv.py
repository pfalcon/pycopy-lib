import os


f = os.popen("echo $_PYCOPY_LIB_TESTVAR")
s = f.read()
assert(s == "\n")
os.putenv("_PYCOPY_LIB_TESTVAR", "12345")
f = os.popen("echo $_PYCOPY_LIB_TESTVAR")
s = f.read()
print(repr(s))
assert s == "12345\n"
