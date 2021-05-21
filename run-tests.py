#!/usr/bin/env python3
# Pycopy will pick up glob from the current dir otherwise.
import sys
sys.path.pop(0)

import glob
import os


cnt_pass = 0
cnt_fail = 0


def run_one(fname, is_cpython):
    global cnt_pass, cnt_fail
    org_fname = fname
    path = "."
    if "/" in fname:
        path, fname = fname.rsplit("/", 1)
    print("%s: " % org_fname, end="")
    sys.stdout.flush()

    extra_args = ""
    if os.path.exists(org_fname + ".args"):
        with open(org_fname + ".args") as f:
            extra_args = f.readline().rstrip()
    interp = "python3" if is_cpython else "pycopy"
    cmd = "cd %s; %s%s %s >/dev/null" % (path, interp, extra_args, fname)
    #print(cmd)
    #return
    st = os.system(cmd)
    if st == 0:
        print("pass")
        cnt_pass += 1
    else:
        print("FAIL")
        cnt_fail += 1


is_cpython = "cpython-" in os.getcwd()

cnt = 0
for fname in glob.iglob("**/test*.py", recursive=True):
    if fname.startswith("_/") or "/_/" in fname:
        continue
    if "testdata" in fname or "benchmark" in fname:
        continue
    run_one(fname, is_cpython or "cpython-" in fname)
    cnt += 1
    if cnt >= 1000:
        break


print("Passed: %d, failed: %d" % (cnt_pass, cnt_fail))
