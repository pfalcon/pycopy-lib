#!/usr/bin/env micropython
#
# Script to install modules from pycopy-lib tree locally.
#
# This module is part of pycopy-lib https://github.com/pfalcon/pycopy-lib
# project.
#
# Copyright (c) 2019 Paul Sokolovsky
#
# The MIT License
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
sys.path.pop(0)
import glob
import os
import shutil


# First check for installability - paths which don't here, aren't even reported.
def should_install_1(f):
    if not f.endswith(".py"):
        return False
    if f.endswith("/setup.py"):
        return False
    if "/testdata" in f:
        return False
    if "/_/" in f:
        return False
    return True


# Second check for installability
def should_install_2(f):
    if "/example" in f:
        return False
    if "/test_" in f:
        return False
    if "/_tool_" in f:
        return False
    return True


mod = sys.argv[1]

if mod.startswith("cpython-"):
    dest_dir = "~/.local/lib/python3.6/site-packages"
else:
    dest_dir = "~/.micropython/lib"

dest_dir = os.path.expanduser(dest_dir)

for f in glob.iglob(mod + "/**", recursive=True):
    if not should_install_1(f):
        continue

    if not should_install_2(f):
        print("#", f)
        continue

    relpath = f[len(mod):]
    dest = dest_dir + relpath
    print(dest)
    try:
        os.makedirs(os.path.dirname(dest))
    except OSError:
        pass
    shutil.copyfile(f, dest)
