import py_compile

py_compile.compile("test.py", "test.mpy2")
# Check that the file is there
open("test.mpy2").close()
