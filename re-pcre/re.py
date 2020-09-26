# This file is part of the standard library of Pycopy project, minimalist
# and lightweight Python implementation.
#
# https://github.com/pfalcon/pycopy
# https://github.com/pfalcon/pycopy-lib
#
# The MIT License (MIT)
#
# Copyright (c) 2014-2020 Paul Sokolovsky
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

from pycopy import const
import sys
import ffilib
import uarray as array


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

# int pcre_get_stringnumber(const pcre *code, const char *name);
pcre_get_stringnumber = pcre.func("i", "pcre_get_stringnumber", "PP")


IGNORECASE = I = 1
MULTILINE = M = 2
DOTALL = S = 4
VERBOSE = X = 8
PCRE_ANCHORED = 0x10
# Ignored
LOCALE = L = 0

# ASCII is a special value ditinguishable from 0
ASCII = A = 0x4000
UNICODE = U = 0x800

PCRE_INFO_CAPTURECOUNT = 2

_UNESCAPE_DICT = const({
    b"\\": b"\\", b"n": b"\n", b"r": b"\r", b"t": b"\t",
    b"v": b"\v", b"f": b"\f", b"a": b"\a", b"b": b"\b"
})


class error(Exception):
    pass


class PCREMatch:

    def __init__(self, patobj, s, is_str, num_matches, offsets):
        self.patobj = patobj
        self.s = s
        self.is_str = is_str
        self.num = num_matches
        self.offsets = offsets

    def _has_group(self, i):
        return i < len(self.offsets) >> 1

    def substr(self, i, default=None):
        if isinstance(i, (str, bytes)):
            n = i
            i = pcre_get_stringnumber(self.patobj, n)
            if i < 0:
                raise IndexError("no such group: %s" % n)
        i <<= 1
        beg = self.offsets[i]
        if beg == -1:
            return default
        s = self.s[beg:self.offsets[i + 1]]
        if self.is_str:
            s = s.decode()
        return s

    def group(self, *n):
        if not n:
            return self.substr(0)
        if len(n) == 1:
            return self.substr(n[0])
        return tuple(self.substr(i) for i in n)

    def groups(self, default=None):
        return tuple(self.substr(i + 1, default) for i in range(self.num - 1))

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
        return PCREMatch(self.obj, s, is_str, cap_count + 1, ov)

    def match(self, s, pos=0, endpos=-1):
        return self.search(s, pos, endpos, PCRE_ANCHORED)

    def _handle_repl_escapes(self, repl, match):

        def handle_escape(esc_match):
            gr = None
            e = esc_match.group(1)
            if e.startswith("0"):
                # Octal escape
                return chr(int(e, 8))
            elif e.startswith("g"):
                gr = e[2:-1]
            elif e.isdigit():
                is_oct = False
                if e.startswith("0"):
                    is_oct = True
                elif len(e) >= 3:
                    try:
                        int(e[:3], 8)
                        is_oct = True
                    except:
                        pass

                if is_oct:
                    rest = e[3:]
                    e = e[:3]
                    val = int(e, 8)
                    if val > 0xff:
                        raise error(r"octal escape value \%s outside of range 0-0o377" % e.decode(), None, 0)
                    return chr(val).encode() + rest

                rest = e[2:]
                e = e[:2]
                gr = int(e)
                if match._has_group(gr):
                    return (match.group(gr) or b"") + rest
                else:
                    raise error("invalid group reference")
            else:
                r = _UNESCAPE_DICT.get(e)
                if r is None:
                    return b"\\" + e
                return r

            if gr.isdigit():
                gr = int(gr)
            return match.group(gr) or b""

        return sub(r"\\(0[0-7]*|\d+|g<.+?>|.)", handle_escape, repl)

    def subn(self, repl, s, count=0):
        is_str = isinstance(s, str)
        if is_str:
            s = s.encode()

        res = b""
        pos = 0
        cnt_rpl = 0
        finish = len(s)
        while pos <= finish:
            m = self.search(s, pos)
            if not m:
                res += s[pos:]
                break
            beg, end = m.span()
            res += s[pos:beg]
            if callable(repl):
                res += repl(m)
            elif "\\" in repl:
                res += self._handle_repl_escapes(repl, m)
            else:
                res += repl
            cnt_rpl += 1

            pos = end
            if beg == end:
                # Have progress on empty matches
                res += s[pos:pos + 1]
                pos += 1

            if count != 0:
                count -= 1
                if count == 0:
                    res += s[pos:]
                    break

        if is_str:
            res = res.decode()
        return (res, cnt_rpl)

    def sub(self, repl, s, count=0):
        res, cnt = self.subn(repl, s, count)
        return res

    def split(self, s, maxsplit=0):
        is_str = isinstance(s, str)
        if is_str:
            s = s.encode()

        res = []
        while True:
            m = self.search(s)
            g = None
            if m:
                g = m.group(0)
            if not m or not g:
                res.append(s)
                break
            beg, end = m.span(0)
            res.append(s[:beg])
            if m.num > 1:
                res.extend(m.groups())
            s = s[end:]
            if maxsplit > 0:
                maxsplit -= 1
                if maxsplit == 0:
                    res.append(s)
                    break

        if is_str:
            for x in res:
                if x is not None:
                    x.__class__ = str

        return res

    def findall(self, s, pos=0, endpos=-1):
        if endpos != -1:
            s = s[:endpos]

        is_str = isinstance(s, str)
        if is_str:
            s = s.encode()

        res = []
        finish = len(s)
        while pos <= finish:
            m = self.search(s, pos)
            if not m:
                break
            if m.num == 1:
                res.append(m.group(0))
            elif m.num == 2:
                res.append(m.group(1))
            else:
                # Will be modified inplace, so must be copy of literal
                x = b""[:]
                res.append(m.groups(x))
            beg, end = m.span(0)
            pos = end
            if beg == end:
                # Have progress on empty matches
                pos += 1

        if is_str:
            for x in res:
                if isinstance(x, tuple):
                    for x1 in x:
                        x1.__class__ = str
                else:
                    x.__class__ = str

        return res

    def finditer(self, s, pos=0, endpos=-1):
        if endpos != -1:
            s = s[:endpos]
        res = []
        finish = len(s)
        while pos <= finish:
            m = self.search(s, pos)
            if not m:
                break
            yield m
            beg, end = m.span(0)
            pos = end
            if beg == end:
                # Have progress on empty matches
                pos += 1


def _check_compiled_flags(flags):
        if flags:
            raise ValueError("cannot process flags argument with a compiled pattern")


def compile(pattern, flags=0):
    if isinstance(pattern, PCREPattern):
        _check_compiled_flags(flags)
        return pattern

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
    if isinstance(pattern, PCREPattern):
        _check_compiled_flags(flags)
        r = pattern
    else:
        r = compile(pattern, flags)
    return r.search(string)


def match(pattern, string, flags=0):
    if isinstance(pattern, PCREPattern):
        _check_compiled_flags(flags)
        r = pattern
    else:
        r = compile(pattern, flags | PCRE_ANCHORED)
    return r.match(string)


def sub(pattern, repl, s, count=0, flags=0):
    r = compile(pattern, flags)
    return r.sub(repl, s, count)


def subn(pattern, repl, s, count=0, flags=0):
    r = compile(pattern, flags)
    return r.subn(repl, s, count)


def split(pattern, s, maxsplit=0, flags=0):
    r = compile(pattern, flags)
    return r.split(s, maxsplit)

def findall(pattern, s, flags=0):
    if isinstance(pattern, PCREPattern):
        _check_compiled_flags(flags)
        r = pattern
    else:
        r = compile(pattern, flags)
    return r.findall(s)

def finditer(pattern, s, flags=0):
    r = compile(pattern, flags)
    return r.finditer(s)


def escape(s):
    if isinstance(s, str):
        res = ""
        for c in s:
            if '0' <= c <= '9' or 'A' <= c <= 'Z' or 'a' <= c <= 'z' or c == '_':
                res += c
            else:
                res += "\\" + c
    else:
        res = b""
        for c in s:
            c = bytes([c])
            if b'0' <= c <= b'9' or b'A' <= c <= b'Z' or b'a' <= c <= b'z' or c == b'_':
                res += c
            else:
                res += b"\\" + c
    return res


def purge():
    pass
