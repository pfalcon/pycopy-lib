import sys
import os
import glob


def handle_one(f):
    rc = os.system("python3.6 example_ast_parse_cpy.py %s >%s.cpy" % (f, f))
    assert rc == 0

    rc = os.system("pycopy -X heapsize=34M example_ast_parse_stream.py %s >%s.upy" % (f, f))
    if rc != 0:
        print("%s: FAIL" % f)
        return False
    rc = os.system("diff -u %s.cpy %s.upy" % (f, f))
    if rc != 0:
        print("%s: error" % f)
        return False
    print("%s: ok" % f)
    return True


errors = False

for f in sorted(glob.glob("testdata/*.py")):
    e = handle_one(f)
    errors = errors or not e

if errors:
    print("FAILED")

sys.exit(int(errors))
