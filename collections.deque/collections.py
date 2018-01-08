'''
DESCRIPTION
    This module provides a double ended queue ---the deque class---
    for MicroPython. The module is imported the same way as in CPython.

    The deque class is an extension of the list object class.
    By consequence, all list methods (including indexing) are inherited.

    At any time, setting the `maxlen` property to an integer will limit the
    length of the given deque during append operations.


USAGE
    import collections
    d = collections.deque()
    d.maxlen = 5


COPYRIGHT
    Copyright (C) 2017-2018  Serge Y. Stroobandt


LICENSE
    The MIT License (MIT)

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.


CONTACT
    echo c2VyZ2VAc3Ryb29iYW5kdC5jb20K |base64 -d
'''


class deque(list):

    def __init__(self):
        super().__init__()
        self.maxlen = None

    def popleft(self):
        return self.pop(0)

    def popright(self):
        return self.pop()

    def append(self, item):
        self.append(item)
        if self.maxlen:
            while len(self) > self.maxlen:
                self.popleft()

    def appendleft(self, item):
        self.insert(0, item)
        if self.maxlen:
            while len(self) > self.maxlen:
                self.popright()

    def __str__(self):
        return 'deque({})'.format(self)
