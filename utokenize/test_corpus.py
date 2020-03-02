import sys
import os
import glob


def handle_one(f):
    rc = os.system("pycopy example_test_dump.py %s >%s.upy" % (f, f))
    if rc != 0:
        print("%s: FAIL" % f)
        return False
    rc = os.system("diff -u %s.cpy %s.upy" % (f, f))
    if rc != 0:
        print("%s: error" % f)
        return False
    print("%s: ok" % f)
    return True


if len(sys.argv) > 1 and sys.argv[1] == "--make-expected":
    for f in glob.glob("testdata/*.py"):
        rc = os.system("python3.6 example_test_dump_cpy.py %s >%s.cpy" % (f, f))
        assert rc == 0
    sys.exit()


errors = False

for f in glob.glob("testdata/*.py"):
    e = handle_one(f)
    errors = errors or not e

sys.exit(int(errors))
