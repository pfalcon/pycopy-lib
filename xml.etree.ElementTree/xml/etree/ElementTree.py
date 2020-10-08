# This file is part of the standard library of Pycopy project, minimalist
# and lightweight Python implementation.
#
# https://github.com/pfalcon/pycopy
# https://github.com/pfalcon/pycopy-lib
#
# The MIT License (MIT)
#
# Copyright (c) 2018-2020 Paul Sokolovsky
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

import io
import xmltok2


class ParseError(Exception):
    pass


class Element:

    def __init__(self):
        self.tag = None
        self.attrib = {}
        self.text = None
        self.tail = None
        self._children = []

    def __getitem__(self, i):
        return self._children[i]

    def __len__(self):
        return len(self._children)

    def append(self, el):
        self._children.append(el)

    def get(self, key, default=None):
        return self.attrib.get(key, default)

    def set(self, key, value):
        self.attrib[key] = value

    def write(self, file):
        assert self.tag is not None
        file.write("<%s" % self.tag)
        for k, v in self.attrib.items():
            file.write(' {}="{}"'.format(k, v))
        file.write(">")
        if self.text is not None:
            file.write(self.text)
        for t in self._children:
            t.write(file)
        file.write("</%s>" % self.tag)
        if self.tail is not None:
            file.write(self.tail)


class ElementTree:

    def __init__(self, root):
        self.root = root

    def getroot(self):
        return self.root

    def write(self, file):
        self.root.write(file)
        file.write("\n")


def parse_el(stream):
    stack = []
    root = None
    last = None

    for ev in xmltok2.tokenize(stream):
        typ = ev[0]

        if typ == xmltok2.START_TAG:
            el = Element()
            el.tag = ev[2]
            if not stack:
                root = el
            else:
                stack[-1]._children.append(el)
            stack.append(el)
            last = None

        elif typ == xmltok2.ATTR:
            # Ignore attrs of processing instructions
            if stack:
                stack[-1].attrib[ev[2]] = ev[3]

        elif typ == xmltok2.TEXT:
            if last is None:
                stack[-1].text = ev[1]
            else:
                last.tail = ev[1]

        elif typ == xmltok2.END_TAG:
            if stack[-1].tag != ev[2]:
                raise ParseError("mismatched tag: /%s (expected: /%s)" % (ev[1][1], stack[-1].tag))
            last = stack.pop()

    return root


def parse(source):
    return ElementTree(parse_el(source))


def fromstring(data):
    buf = io.StringIO(data)
    return parse_el(buf)
