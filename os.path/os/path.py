import os
import ffilib


sep = "/"

def normcase(s):
    return s

def normpath(s):
    return s

def abspath(s):
    if s[0] != "/":
        return os.getcwd() + "/" + s
    return s

def join(*args):
    is_bytes = isinstance(args[0], bytes)
    res = ""
    for a in args:
        if is_bytes:
            a = a.decode()
        if not res or a.startswith("/"):
            res = a
        else:
            res += "/" + a
    res = res.replace("//", "/")
    if is_bytes:
        return res.encode()
    return res

def split(path):
    if path == "":
        return ("", "")
    r = path.rsplit("/", 1)
    if len(r) == 1:
        return ("", path)
    head = r[0] #.rstrip("/")
    if not head:
        head = "/"
    return (head, r[1])

def splitdrive(path):
    return "", path

def dirname(path):
    return split(path)[0]

def basename(path):
    return split(path)[1]

def exists(path):
    return os.access(path, os.F_OK)

# TODO
lexists = exists

def isfile(path):
    import stat
    try:
        mode = os.stat(path)[0]
        return stat.S_ISREG(mode)
    except OSError:
        return False

def isdir(path):
    import stat
    try:
        mode = os.stat(path)[0]
        return stat.S_ISDIR(mode)
    except OSError:
        return False

def islink(path):
    import stat
    try:
        mode = os.lstat(path)[0]
        return stat.S_ISLNK(mode)
    except OSError:
        return False

def realpath(path):
    libc = ffilib.libc()
    if isinstance(path, str) or isinstance(path, bytes):
        realpath_ = libc.func("s", "realpath", "ss")
        # XXX: memory leak! should free() returned pointer, see man realpath
        return realpath_(path, None)
    raise TypeError

def expanduser(s):
    if s == "~" or s.startswith("~/"):
        h = os.getenv("HOME")
        return h + s[1:]
    if s[0] == "~":
        # Sorry folks, follow conventions
        return "/home/" + s[1:]
    return s
