# uos2 - more POSIX OS functions than builtin "uos" module, but no additional
# baggage as in CPython's "os".
#
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

import uos
import uarray
import errno
import ffilib


R_OK = const(4)
W_OK = const(2)
X_OK = const(1)
F_OK = const(0)

O_ACCMODE  = const(0o0000003)
O_RDONLY   = const(0o0000000)
O_WRONLY   = const(0o0000001)
O_RDWR     = const(0o0000002)
O_CREAT    = const(0o0000100)
O_EXCL     = const(0o0000200)
O_NOCTTY   = const(0o0000400)
O_TRUNC    = const(0o0001000)
O_APPEND   = const(0o0002000)
O_NONBLOCK = const(0o0004000)

WNOHANG = const(1)


_libc = ffilib.libc()

_getcwd = _libc.func("s", "getcwd", "si")
_chdir = _libc.func("i", "chdir", "s")
_mkdir = _libc.func("i", "mkdir", "si")
_rmdir = _libc.func("i", "rmdir", "s")
_rename = _libc.func("i", "rename", "ss")
_unlink = _libc.func("i", "unlink", "s")
_access = _libc.func("i", "access", "si")
_utimes = _libc.func("i", "utimes", "sP")

_open = _libc.func("i", "open", "sii")
_read = _libc.func("i", "read", "ipi")
_write = _libc.func("i", "write", "iPi")
_lseek = _libc.func("l", "lseek", "ili")
_close = _libc.func("i", "close", "i")

_dup2 = _libc.func("i", "dup2", "ii")
_pipe = _libc.func("i", "pipe", "p")

getpid = _libc.func("i", "getpid", "")  # no wrapper (nw)
_exit = _libc.func("v", "_exit", "i")  # nw
_kill = _libc.func("i", "kill", "ii")
_fork = _libc.func("i", "fork", "")
_waitpid = _libc.func("i", "waitpid", "ipi")
_execvp = _libc.func("i", "execvp", "PP")
_system = _libc.func("i", "system", "s")

getpgid = _libc.func("i", "getpgid", "i")  # nw
setsid = _libc.func("i", "setsid", "")  # nw

_getenv = _libc.func("s", "getenv", "P")
_putenv = _libc.func("i", "putenv", "s")

strerror = _libc.func("s", "strerror", "i")  # nw


def check_error(ret):
    # Return True is error was EINTR (which usually means that OS call
    # should be restarted).
    if ret == -1:
        e = uos.errno()
        if e == errno.EINTR:
            return True
        raise OSError(e)


if hasattr(uos, "getcwd"):
    getcwd = uos.getcwd
else:
    def getcwd():
        buf = bytearray(512)
        return _getcwd(buf, 512)


if hasattr(uos, "chdir"):
    chdir = uos.chdir
else:
    def chdir(dir):
        r = _chdir(dir)
        check_error(r)


def mkdir(name, mode=0o777):
    e = _mkdir(name, mode)
    check_error(e)


if hasattr(uos, "rmdir"):
    rmdir = uos.rmdir
else:
    def rmdir(name):
        e = _rmdir(name)
        check_error(e)


if hasattr(uos, "rename"):
    rename = uos.rename
else:
    def rename(old, new):
        e = _rename(old, new)
        check_error(e)

if hasattr(uos, "remove"):
    unlink = remove = uos.remove
else:
    def unlink(name):
        e = _unlink(name)
        check_error(e)
    remove = unlink


def access(path, mode):
    return _access(path, mode) == 0


def utime(path, times):
    at_s = int(times[0])
    mt_s = int(times[1])
    at_us = int((times[0] - at_s) * 1000000)
    mt_us = int((times[1] - mt_s) * 1000000)
    arr = uarray.array("L", [at_s, at_us, mt_s, mt_us])
    r = _utimes(path, arr)
    check_error(r)


def open(n, flags, mode=0o777):
    r = _open(n, flags, mode)
    check_error(r)
    return r


def read(fd, n):
    buf = bytearray(n)
    r = _read(fd, buf, n)
    check_error(r)
    return bytes(buf[:r])


def write(fd, buf):
    r = _write(fd, buf, len(buf))
    check_error(r)
    return r


def lseek(fd, pos, how):
    r = _lseek(fd, pos, how)
    check_error(r)
    return r


def close(fd):
    r = _close(fd)
    check_error(r)
    return r


def dup2(o, n):
    r = _dup2(o, n)
    check_error(r)
    return r


def pipe():
    a = uarray.array("i", [0, 0])
    r = _pipe(a)
    check_error(r)
    return a[0], a[1]


def kill(pid, sig):
    r = _kill(pid, sig)
    check_error(r)


def fork():
    r = _fork()
    check_error(r)
    return r


def waitpid(pid, opts):
    a = uarray.array("i", [0])
    r = _waitpid(pid, a, opts)
    check_error(r)
    return r, a[0]


def execvp(f, args):
    import uctypes
    args_ = uarray.array("P", [0] * (len(args) + 1))
    i = 0
    for a in args:
        args_[i] = uctypes.addressof(a)
        i += 1
    r = _execvp(f, args_)
    check_error(r)


def system(c):
    r = _system(c)
    check_error(r)
    return r


def getenv(var, default=None):
    var = _getenv(var)
    if var is None:
        return default
    return var


def putenv(key, value):
    return _putenv(key + "=" + value)
