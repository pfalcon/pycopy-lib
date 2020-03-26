import sys
import os


if len(sys.argv) != 2:
    print("usage: venv ENV_DIR")
    sys.exit(1)

env = sys.argv[1]
os.makedirs(env + "/bin")
with open(env + "/bin/activate", "w") as f:
    f.write("""\
export MICROPYPATH=%s
""" % os.path.abspath(env + "/lib"))
