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


def splitext(path):
    r = path.rsplit(".", 1)
    if len(r) == 1:
        return path, ""
    if not r[0]:
        return path, ""
    return r[0], "." + r[1]


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

def isabs(path):
    return path.startswith("/")

def realpath(path):
    libc = ffilib.libc()
    if isinstance(path, str) or isinstance(path, bytes):
        realpath_ = libc.func("s", "realpath", "ss")
        # XXX: memory leak! should free() returned pointer, see man realpath
        res = realpath_(path, None)
        if res is not None:
            return res
        # Assume that file doesn't exist, return abspath.
        return abspath(path)

    raise TypeError

def expanduser(s):
    if s == "~" or s.startswith("~/"):
        h = os.getenv("HOME")
        return h + s[1:]
    if s[0] == "~":
        # Sorry folks, follow conventions
        return "/home/" + s[1:]
    return s


# From CPython git tag v3.4.10.
# Return the longest prefix of all list elements.
def commonprefix(m):
    "Given a list of pathnames, returns the longest common leading component"
    if not m: return ''
    s1 = min(m)
    s2 = max(m)
    for i, c in enumerate(s1):
        if c != s2[i]:
            return s1[:i]
    return s1


# From CPython git tag v3.4.10.
def relpath(path, start=None):
    """Return a relative version of a path"""

    if not path:
        raise ValueError("no path specified")

    if isinstance(path, bytes):
        curdir = b'.'
        sep = b'/'
        pardir = b'..'
    else:
        curdir = '.'
        sep = '/'
        pardir = '..'

    if start is None:
        start = curdir

    start_list = [x for x in abspath(start).split(sep) if x]
    path_list = [x for x in abspath(path).split(sep) if x]

    # Work out how much of the filepath is shared by start and path.
    i = len(commonprefix([start_list, path_list]))

    rel_list = [pardir] * (len(start_list)-i) + path_list[i:]
    if not rel_list:
        return curdir
    return join(*rel_list)
