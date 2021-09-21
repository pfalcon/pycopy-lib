import os
import time


f = os.popen("echo foo")
data = f.read()
assert data == "foo\n"
f.close()

os.remove("test.file")
f = os.popen("cat > test.file", "w")
f.write("here")
f.close()

# We close the pipe's end, it doesn't mean that the other side actually
# read/processed data in the pipe, give it some time.
time.sleep(0.05)

with open("test.file") as f:
    data = f.read()
    assert data == "here"
