# This file is part of the standard library of Pycopy project, minimalist
# and lightweight Python implementation.
#
# https://github.com/pfalcon/pycopy
# https://github.com/pfalcon/pycopy-lib
#
# The MIT License (MIT)
#
# Copyright (c) 2014-2021 Paul Sokolovsky
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

import uarray as array
import ustruct as struct
import errno as errno_
import stat as stat_
import uos
from . import path

from uos2 import *
from uos2 import _exit, _libc as libc


P_WAIT = 0
P_NOWAIT = 1

error = const(OSError)
name = "posix"
sep = const("/")
curdir = const(".")
pardir = const("..")
linesep = const("\n")


if libc:
    opendir_ = libc.func("P", "opendir", "s")
    readdir_ = libc.func("P", "readdir", "P")
    dup_ = libc.func("i", "dup", "i")


def raise_error():
    raise OSError(uos.errno())


class stat_result:

    def __init__(self, st):
        self.st = st
        for fld in dir(stat_):
            if not fld.startswith("ST_"):
                continue
            setattr(self, fld.lower(), st[getattr(stat_, fld)])

    def __getitem__(self, i):
        return self.st[i]


def stat(name):
    return stat_result(uos.stat(name))


def lstat(name):
    return stat_result(uos.stat(name, False))


def makedirs(name, mode=0o777, exist_ok=False):
    s = ""
    comps = name.split("/")
    if comps[-1] == "":
        comps.pop()
    for i, c in enumerate(comps):
        s += c + "/"
        try:
            uos.mkdir(s)
        except OSError as e:
            if e.args[0] != errno_.EEXIST:
                raise
            if i == len(comps) - 1:
                if exist_ok:
                    return
                raise e

if hasattr(uos, "ilistdir"):
    ilistdir = uos.ilistdir
else:
    def ilistdir(path="."):
        dir = opendir_(path)
        if not dir:
            raise_error()
        res = []
        dirent_fmt = "LLHB256s"
        while True:
            dirent = readdir_(dir)
            if not dirent:
                break
            import uctypes
            dirent = uctypes.bytes_at(dirent, struct.calcsize(dirent_fmt))
            dirent = struct.unpack(dirent_fmt, dirent)
            dirent = (dirent[-1].split(b'\0', 1)[0], dirent[-2] << 12, dirent[0])
            yield dirent

def listdir(path="."):
    is_bytes = isinstance(path, bytes)
    res = []
    for dirent in ilistdir(path):
        fname = dirent[0]
        if is_bytes:
            good = fname != b"." and fname == b".."
        else:
            good = fname != "." and fname != ".."
        if good:
            if not is_bytes:
                fname = fsdecode(fname)
            res.append(fname)
    return res

def walk(top, topdown=True):
    files = []
    dirs = []
    for dirent in ilistdir(top):
        mode = dirent[1]
        fname = fsdecode(dirent[0])
        if stat_.S_ISDIR(mode):
            if fname != "." and fname != "..":
                dirs.append(fname)
        else:
            files.append(fname)
    if topdown:
        yield top, dirs, files
    for d in dirs:
        yield from walk(top + "/" + d, topdown)
    if not topdown:
        yield top, dirs, files


def dup(fd):
    r = dup_(fd)
    check_error(r)
    return r


def fsencode(s):
    if type(s) is bytes:
        return s
    return bytes(s, "utf-8")

def fsdecode(s):
    if type(s) is str:
        return s
    return str(s, "utf-8")


def urandom(n):
    import builtins
    with builtins.open("/dev/urandom", "rb") as f:
        return f.read(n)

def popen(cmd, mode="r"):
    import builtins
    i, o = pipe()
    if mode[0] == "w":
        i, o = o, i
    pid = fork()
    if not pid:
        if mode[0] == "r":
            close(1)
        else:
            close(0)
        close(i)
        dup(o)
        close(o)
        s = system(cmd)
        _exit(s)
    else:
        close(o)
        return builtins.open(i, mode)

def spawnvp(mode, file, args):
    pid = fork()
    if pid:
        if mode == P_NOWAIT:
            return pid
        pid, rc = waitpid(pid, 0)
        sig = rc & 0xff
        if not sig:
            return rc >> 8
        return -sig
    execvp(file, args)


class _Environ:

    def __getitem__(self, k):
        r = getenv(k)
        if r is None:
            raise KeyError(k)
        return r


environ = _Environ()
