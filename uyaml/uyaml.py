# This file is part of the standard library of Pycopy project, minimalist
# and lightweight Python implementation.
#
# https://github.com/pfalcon/pycopy
# https://github.com/pfalcon/pycopy-lib
#
# The MIT License (MIT)
#
# Copyright (c) 2019 Paul Sokolovsky
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

import uio


class YamlParser:

    def __init__(self, f):
        self.f = f
        self.l = None

    def readline(self):
        if self.l is not None:
            l = self.l
            self.l = None
            return l
        return self.f.readline()

    def unreadline(self, l):
#        print("-unread:", l)
        assert self.l is None
        self.l = l

    @staticmethod
    def calc_indent(l):
        indent = 0
        while l[indent] == " ":
            indent += 1
        return indent, l[indent:]

    def detect_block_type(self):
        l = self.readline()
        self.unreadline(l)
        indent, subl = self.calc_indent(l)
        if subl.startswith("- "):
            return list
        else:
            return dict

    def match(self, s):
        if self.pl.startswith(s):
            self.pl = self.pl[len(s):].lstrip()
            return True
        return False

    def expect(self, s):
        assert self.match(s), "Expected %r at %r" % (s, self.pl)

    def eol(self):
        return self.pl == ""

    def expect_eol(self):
        assert self.eol(), repr(self.pl)

    def parse_atomic_with_sep(self, seps=None):
        if self.pl[0] in ("'", '"'):
            sep = self.pl[0]
            i = 1
            while True:
                if i >= len(self.pl):
                    assert 0
                if self.pl[i] == sep:
                    break
                i += 1
            ret = self.pl[1:i]
            self.pl = self.pl[i + 1:].lstrip()
            return ret
        else:
            if not seps:
                ret = self.pl.strip()
                self.pl = ""
                return ret
            for i in range(len(self.pl)):
                if self.pl[i] in seps:
                    # foo:bar is a string
                    if self.pl[i] == ":" and i < len(self.pl) - 1 and not self.pl[i + 1].isspace():
                        continue
                    break
            else:
                i += 1
            ret = self.pl[:i]
            self.pl = self.pl[i:]

            try:
                ret = int(ret, 0)
            except ValueError:
                pass

            return ret

    def parse_inline(self, seps=None):
        if self.match("["):
            res = []
            if self.match("]"):
                return res
            while True:
                el = self.parse_inline((",", "]"))
                res.append(el)
                if self.match("]"):
                    break
                self.expect(",")
            return res
        elif self.match("{"):
            res = {}
            if self.match("}"):
                return res
            while True:
                key = self.parse_inline((":",))
                self.expect(":")
                val = self.parse_inline((",", "}"))
                res[key] = val
                if self.match("}"):
                    break
                self.expect(",")
            return res
        else:
            return self.parse_atomic_with_sep(seps)

    def parse_block(self, target_indent):
        res = None
        while True:
            rawl = self.readline()
            if not rawl:
                return res
            indent, l = self.calc_indent(rawl)
            if indent != target_indent:
                self.unreadline(rawl)
                return res

            l = l.rstrip()
            self.pl = l
            as_list = False
            if self.match("- "):
                as_list = True
                if res is None:
                    res = []

            if as_list and self.pl.startswith("- "):
                rawl = rawl.replace("- ", "  ", 1)
                self.unreadline(rawl)
                r = self.parse_block(target_indent + 2)
            else:
                r = self.parse_inline((":",))

            if self.match(":"):
                if res is None:
                    res = {}
                elif isinstance(res, list):
                    self.unreadline(rawl)
                    return res

                if self.eol():
                    nextl = self.readline()
                    nexti, _ = self.calc_indent(nextl)
                    self.unreadline(nextl)
                    subobj = self.parse_block(nexti)
                    res[r] = subobj
                else:
                    res[r] = self.parse_inline()
            else:
                if not as_list and res is None:
                    assert target_indent == 0
                    return r
                res.append(r)
                self.expect_eol()

    def parse(self):
        return self.parse_block(0)


def dump(data, stream, sort_keys=True, indent=0):
    def do_indent(indent):
        stream.write("  " * indent)

    if isinstance(data, list):
        for i in data:
            do_indent(indent - 1)
            stream.write("- ")
            dump(i, stream, sort_keys, indent + 1)
    elif isinstance(data, dict):
        it = data.items()
        if sort_keys:
            it = sorted(it)
        for k, v in it:
            do_indent(indent)
            stream.write(str(k))
            if isinstance(v, (list, dict)):
                stream.write(":\n")
                dump(v, stream, sort_keys, indent + 1)
            else:
                stream.write(": ")
                dump(v, stream, sort_keys, indent + 1)
    else:
        stream.write(str(data))
        stream.write("\n")
