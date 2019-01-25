import sys
import os


env = sys.argv[1]
os.makedirs(env + "/bin")
with open(env + "/bin/activate", "w") as f:
    f.write("""\
export MICROPYPATH=%s
""" % os.path.abspath(env + "/lib"))
