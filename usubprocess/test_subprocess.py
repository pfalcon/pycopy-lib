import usubprocess as subprocess


p = subprocess.Popen("echo output", shell=True)
res = p.communicate()
print(res)
assert res == (None, None)
retc = p.wait()
print(retc)
assert retc == 0

p = subprocess.Popen(["echo", "output"])
res = p.communicate()
print(res)
assert res == (None, None)
retc = p.wait()
print(retc)
assert retc == 0

p = subprocess.Popen(["false"])
res = p.communicate()
print(res)
assert res == (None, None)
retc = p.wait()
print(retc)
assert retc == 1

p = subprocess.Popen("false", shell=True)
retc = p.wait()
print(retc)
assert retc == 1

p = subprocess.Popen(["echo", "output"], stdout=subprocess.PIPE)
res = p.communicate()
print(res)
assert res == (b"output\n", None)
