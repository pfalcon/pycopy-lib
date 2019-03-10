import sys
import ffilib
import array


pcre = ffilib.open("libpcre")

#       pcre *pcre_compile(const char *pattern, int options,
#            const char **errptr, int *erroffset,
#            const unsigned char *tableptr);
pcre_compile = pcre.func("p", "pcre_compile", "sipps")

#       int pcre_exec(const pcre *code, const pcre_extra *extra,
#            const char *subject, int length, int startoffset,
#            int options, int *ovector, int ovecsize);
pcre_exec = pcre.func("i", "pcre_exec", "PPsiiipi")

#       int pcre_fullinfo(const pcre *code, const pcre_extra *extra,
#            int what, void *where);
pcre_fullinfo = pcre.func("i", "pcre_fullinfo", "PPip")


IGNORECASE = I = 1
MULTILINE = M = 2
DOTALL = S = 4
VERBOSE = X = 8
PCRE_ANCHORED = 0x10

# ASCII is a special value ditinguishable from 0
ASCII = A = 0x4000
UNICODE = U = 0x800

PCRE_INFO_CAPTURECOUNT = 2


class error(Exception):
    pass


class PCREMatch:

    def __init__(self, s, is_str, num_matches, offsets):
        self.s = s
        self.is_str = is_str
        self.num = num_matches
        self.offsets = offsets

    def sub(self, i):
        s = self.s[self.offsets[i]:self.offsets[i + 1]]
        if self.is_str:
            s = s.decode()
        return s

    def group(self, *n):
        if not n:
            return self.sub(0)
        if len(n) == 1:
            return self.sub(n[0] * 2)
        return tuple(self.sub(i * 2) for i in n)

    def groups(self, default=None):
        assert default is None
        return tuple(self.group(i + 1) for i in range(self.num - 1))

    def start(self, n=0):
        return self.offsets[n*2]

    def end(self, n=0):
        return self.offsets[n*2+1]

    def span(self, n=0):
        return self.offsets[n*2], self.offsets[n*2+1]


class PCREPattern:

    def __init__(self, compiled_ptn):
        self.obj = compiled_ptn

    def search(self, s, pos=0, endpos=-1, _flags=0):
        assert endpos == -1, "pos: %d, endpos: %d" % (pos, endpos)
        buf = array.array('i', [0])
        pcre_fullinfo(self.obj, None, PCRE_INFO_CAPTURECOUNT, buf)
        cap_count = buf[0]

        ov = array.array('i', [0, 0, 0] * (cap_count + 1))
        is_str = isinstance(s, str)
        if is_str:
            s = s.encode()
        num = pcre_exec(self.obj, None, s, len(s), pos, _flags, ov, len(ov))
        if num == -1:
            # No match
            return None
        # We don't care how many matching subexpressions we got, we
        # care only about total # of capturing ones (including empty)
        return PCREMatch(s, is_str, cap_count + 1, ov)

    def match(self, s, pos=0, endpos=-1):
        return self.search(s, pos, endpos, PCRE_ANCHORED)

    def sub(self, repl, s, count=0):
        if not callable(repl):
            assert "\\" not in repl, "Backrefs not implemented"
        res = ""
        while s:
            m = self.search(s)
            if not m:
                return res + s
            beg, end = m.span()
            res += s[:beg]
            if callable(repl):
                res += repl(m)
            else:
                res += repl
            s = s[end:]
            if count != 0:
                count -= 1
                if count == 0:
                    return res + s
        return res

    def split(self, s, maxsplit=0):
        res = []
        while True:
            m = self.search(s)
            g = None
            if m:
                g = m.group(0)
            if not m or not g:
                res.append(s)
                return res
            beg, end = m.span(0)
            res.append(s[:beg])
            if m.num > 1:
                res.extend(m.groups())
            s = s[end:]
            if maxsplit > 0:
                maxsplit -= 1
                if maxsplit == 0:
                    res.append(s)
                    return res

    def findall(self, s):
        res = []
        start = 0
        while True:
            m = self.search(s, start)
            if not m:
                return res
            if m.num == 1:
                res.append(m.group(0))
            elif m.num == 2:
                res.append(m.group(1))
            else:
                res.append(m.groups())
            beg, end = m.span(0)
            start = end


def compile(pattern, flags=0):
    if flags & ASCII:
        flags &= ~ASCII
    else:
        if isinstance(pattern, str):
            flags |= UNICODE
    # Assume that long can hold a pointer
    errptr = array.array("l", [0])
    erroffset = array.array("i", [0])
    regex = pcre_compile(pattern, flags, errptr, erroffset, None)
    if not regex:
        raise error("couldn't compile pattern: %s" % pattern)
    return PCREPattern(regex)


def search(pattern, string, flags=0):
    r = compile(pattern, flags)
    return r.search(string)


def match(pattern, string, flags=0):
    r = compile(pattern, flags | PCRE_ANCHORED)
    return r.search(string)


def sub(pattern, repl, s, count=0, flags=0):
    r = compile(pattern, flags)
    return r.sub(repl, s, count)


def split(pattern, s, maxsplit=0, flags=0):
    r = compile(pattern, flags)
    return r.split(s, maxsplit)

def findall(pattern, s, flags=0):
    r = compile(pattern, flags)
    return r.findall(s)


def escape(s):
    res = ""
    for c in s:
        if '0' <= c <= '9' or 'A' <= c <= 'Z' or 'a' <= c <= 'z' or c == '_':
            res += c
        else:
            res += "\\" + c
    return res
