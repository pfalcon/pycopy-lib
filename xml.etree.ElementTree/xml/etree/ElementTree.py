import io
import xmltok


class ParseError(Exception):
    pass


class Element:

    def __init__(self):
        self.tag = None
        self.attrib = {}
        self.text = None
        self._children = []

    def __getitem__(self, i):
        return self._children[i]

    def __len__(self):
        return len(self._children)


class ElementTree:

    def __init__(self, root):
        self.root = root

    def getroot(self):
        return self.root


def parse_el(stream):
    stack = []
    root = None

    for ev in xmltok.tokenize(stream):
        typ = ev[0]

        if typ == xmltok.START_TAG:
            el = Element()
            el.tag = ev[1][1]
            if not stack:
                root = el
            else:
                stack[-1]._children.append(el)
            stack.append(el)

        elif typ == xmltok.ATTR:
            stack[-1].attrib[ev[1][1]] = ev[2]

        elif typ == xmltok.TEXT:
            stack[-1].text = ev[1]

        elif typ == xmltok.END_TAG:
            if stack[-1].tag != ev[1][1]:
                raise ParseError("mismatched tag: /%s (expected: /%s)" % (ev[1][1], stack[-1].tag))
            stack.pop()

    return root


def parse(source):
    return ElementTree(parse_el(source))


def fromstring(data):
    buf = io.StringIO(data)
    return parse_el(buf)
