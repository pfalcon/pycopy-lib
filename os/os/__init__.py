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
import uctypes
import errno as errno_
import stat as stat_
import uos
from . import path

from uos2 import *
from uos2 import _exit, _libc as libc

PathLike = path.PathLike

P_WAIT = 0
P_NOWAIT = 1

error = OSError
name = "posix"
sep = "/"
curdir = "."
pardir = ".."
devnull = "/dev/null"
linesep = "\n"


if libc:
    opendir_ = libc.func("P", "opendir", "s")
    readdir_ = libc.func("P", "readdir", "P")
    dup_ = libc.func("i", "dup", "i")
    _execvpe = libc.func("i", "execvpe", "PPP")  # non-POSIX
    _environ_ptr = libc.var("P", "environ")


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


def WIFSIGNALED(st):
    return st & 0x7f != 0

def WIFEXITED(st):
    return st & 0x7f == 0

def WEXITSTATUS(st):
    return st >> 8

def WTERMSIG(st):
    return st & 0x7f


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


def execvpe(f, args, env):
    import uctypes
    args_ = uarray.array("P", [0] * (len(args) + 1))
    i = 0
    for a in args:
        args_[i] = uctypes.addressof(a)
        i += 1
    env_ = uarray.array("P", [0] * (len(env) + 1))
    i = 0
    if isinstance(env, list):
        for s in env:
            env_[i] = uctypes.addressof(s)
            i += 1
    else:
        env_l = []  # so strings weren't gc'ed
        for k, v in env.items():
            s = "%s=%s" % (k, v)
            env_l.append(s)
            env_[i] = uctypes.addressof(s)
            i += 1
    r = _execvpe(f, args_, env_)
    check_error(r)


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


def closerange(low, high):
    for fd in range(low, high):
        try:
            close(fd)
        except OSError:
            pass


def fpathconf(fd, name):
    if name == "PC_PIPE_BUF":
        return 512
    raise ValueError


_ENV_STRUCT = {
    "arr": (uctypes.ARRAY, 4096, (uctypes.PTR, uctypes.UINT8))
}


class _Environ(object):

    def __init__(self):
        self._data = dict()
        env = uctypes.struct(_environ_ptr.get(), _ENV_STRUCT)
        try:
            uctypes.bytestring_at
        except AttributeError:
            def getter(addr):
                n = 0
                while True:
                    if uctypes.bytes_at(int(addr)+n,1)[0] == 0:
                        break
                    n += 1
                return uctypes.bytearray_at(int(addr),n).decode()
        else:
            def getter(addr):
                return uctypes.bytestring_at(int(addr)).decode()

            
        for i in range(4096):
            if int(env.arr[i]) == 0:
                break
            s = getter(int(env.arr[i]))
            k, v = s.split("=", 1)
            self._data[k] = v
        self.__getitem__ = self._data.__getitem__

    def __setitem__(self, k, v):
        try:
            uos2.putenv(k.encode(), v.encode())
        except AttributeError:
            # XXX is this right?
            pass
        self._data[k] = v


environ = _Environ()
