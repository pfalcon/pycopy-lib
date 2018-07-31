TEXT = "TEXT"
START_TAG = "START_TAG"
#START_TAG_DONE = "START_TAG_DONE"
END_TAG = "END_TAG"
PI = "PI"
#PI_DONE = "PI_DONE"
ATTR = "ATTR"
#ATTR_VAL = "ATTR_VAL"

class XMLSyntaxError(Exception):
    pass

class XMLTokenizer:

    def __init__(self, f):
        self.f = f
        self.nextch()

    def curch(self):
        return self.c

    def getch(self):
        c = self.c
        self.nextch()
        return c

    def eof(self):
        return self.c == ""

    def nextch(self):
        self.c = self.f.read(1)
        if not self.c:
            raise StopIteration
        return self.c

    def skip_ws(self):
        while self.curch().isspace():
            self.nextch()

    def isident(self):
        self.skip_ws()
        return self.curch().isalpha()

    def getident(self):
        self.skip_ws()
        ident = ""
        while True:
            c = self.curch()
            if not(c.isalpha() or c.isdigit() or c in "_-."):
                break
            ident += self.getch()
        return ident

    def putnsident(self, res):
        ns = ""
        ident = self.getident()
        if self.curch() == ":":
            self.nextch()
            ns = ident
            ident = self.getident()
        res[1] = ns
        res[2] = ident

    def match(self, c):
        self.skip_ws()
        if self.curch() == c:
            self.nextch()
            return True
        return False

    def expect(self, c):
        if not self.match(c):
            raise XMLSyntaxError

    def lex_attrs_till(self, res):
        while self.isident():
            res[0] = ATTR
            self.putnsident(res)
            self.expect("=")
            self.expect('"')
            val = ""
            while self.curch() != '"':
                val += self.getch()
            self.expect('"')
            res[3] = val
            yield res
            res[3] = None

    def tokenize(self):
        res = [None, None, None, None]
        while not self.eof():
            if self.match("<"):
                if self.match("/"):
                    res[0] = END_TAG
                    self.putnsident(res)
                    yield res
                    self.expect(">")
                elif self.match("?"):
                    res[0] = PI
                    res[1] = self.getident()
                    yield res
                    yield from self.lex_attrs_till(res)
                    self.expect("?")
                    self.expect(">")
                elif self.match("!"):
                    self.expect("-")
                    self.expect("-")
                    last3 = ''
                    while True:
                        last3 = last3[-2:] + self.getch()
                        if last3 == "-->":
                            break
                else:
                    res[0] = START_TAG
                    self.putnsident(res)
                    yield res
                    yield from self.lex_attrs_till(res)
                    if self.match("/"):
                        yield (END_TAG, tag)
                    self.expect(">")
            else:
                text = ""
                while self.curch() != "<":
                    text += self.getch()
                if text:
                    res[0] = TEXT
                    res[1] = text
                    res[2] = None
                    yield res


def gfind(gen, pred):
    for i in gen:
        if pred(i):
            return i

def text_of(gen, tag):
    # Return text content of a leaf tag from tokenizer stream
    def match_tag(t):
        if t[0] != START_TAG:
            return False
        if isinstance(tag, tuple):
            return t[1] == tag[0] and t[2] == tag[1]
        return t[2] == tag

    gfind(gen, match_tag)
    # Assumes no attributes
    res = next(gen)
    assert res[0] == TEXT
    return res[1]

def tokenize(file):
    return XMLTokenizer(file).tokenize()
