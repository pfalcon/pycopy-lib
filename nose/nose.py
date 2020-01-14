# This file is part of the standard library of Pycopy project, minimalist
# and lightweight Python implementation.
#
# https://github.com/pfalcon/pycopy
# https://github.com/pfalcon/pycopy-lib
#
# The MIT License (MIT)
#
# Copyright (c) 2020 Paul Sokolovsky
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys
import os


def main():
    pypath = sys.path + ["."]
    pypath = ":".join(pypath)

    testpath = "."

    for path, dirs, files in os.walk(testpath):

        # Skip dirs with leading dot, like ".venv", etc.
        dirs_new = []
        for d in dirs:
            if d[0] == ".":
                continue
            dirs_new.append(d)
        dirs[:] = dirs_new

        for f in files:
            if not f.startswith("test_") or not f.endswith(".py"):
                continue
            fullname = path + "/" + f
            fullname = fullname[len(testpath) + 1:]
            print(fullname)
            modname = fullname[:-len(".py")]
            modname = modname.replace("/", ".")
            #print(modname)
            m = __import__(modname, None, None, True)
            #print(m)
            for name in dir(m):
                if not name.startswith("test_"):
                    continue
                o = getattr(m, name)
                if callable(o):
                    o()


if __name__ == "__main__":
    main()
