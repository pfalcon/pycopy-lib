import uio
from urllib.urequest import urlopen
import xmltok2
from xmltok2 import START_TAG, END_TAG, TEXT


class Lexer:

    def __init__(self, gen):
        self.gen = gen
        self.next()

    def next(self):
        self.t = next(self.gen)
        #print(self.t)

    def match(self, what):
        res = None
        if what == START_TAG:
            if self.t[0] == START_TAG:
                res = self.t[2]
        elif what == TEXT:
            if self.t[0] == TEXT:
                res = self.t[1]
        elif what.startswith("/"):
            if self.t[0] == END_TAG and self.t[2] == what[1:]:
                res = True
        else:
            if self.t[0] == START_TAG and self.t[2] == what:
                res = True
        if res is not None:
            self.next()
        #print("match(%s)=%s" % (what, res))
        return res

    def expect(self, what):
        res = self.match(what)
        assert res is not None
        return res


class Method:

    def __init__(self, server, name):
        self.server = server
        self.name = name

    def __getattr__(self, attr):
        self.name += "." + attr
        return self

    def __call__(self, *args):
        buf = uio.StringIO()
        buf.write("<?xml version='1.0'?>\n<methodCall>\n<methodName>")
        buf.write(self.name)
        buf.write("</methodName>\n<params>\n")
        for a in args:
            buf.write("<param>")
            self.dump(buf, a)
            buf.write("</param>\n")
        buf.write("</params>\n</methodCall>\n")
        if self.server.verbose:
            print(buf.getvalue())
        body = buf.getvalue().encode()

        f = urlopen(self.server.uri, body, "POST")

        try:
            #print(f.read())
            f = uio.TextIOWrapper(f)
            tokenizer = xmltok2.tokenize(f)
            xmltok2.gfind(tokenizer, lambda ev: ev[0] == xmltok2.START_TAG and ev[2] == "param")
            val = self.parse(Lexer(tokenizer))
            return val
        finally:
            #print("*", f.read())
            f.close()

    def dump(self, buf, val):
        buf.write("<value>")
        if isinstance(val, int):
            buf.write("<int>%s</int>" % val)
        elif isinstance(val, str):
            buf.write("<string>%s</string>" % val)
        elif val is None:
            buf.write("<nil/>")
        elif isinstance(val, list):
            buf.write("<array><data>")
            for v in val:
                self.dump(buf, v)
            buf.write("</data></array>")
        else:
            raise NotImplementedError(repr(val))
        buf.write("</value>")

    def parse(self, lex):
        res = None
        lex.expect("value")
        typ = lex.expect(START_TAG)
        if typ == "array":
            res = []
            lex.expect("data")
            while not lex.match("/data"):
                res.append(self.parse(lex))
            lex.expect("/array")
        elif typ == "struct":
            res = {}
            while not lex.match("/struct"):
                lex.expect("member")
                lex.expect("name")
                key = lex.expect(TEXT)
                lex.expect("/name")
                res[key] = self.parse(lex)
                lex.expect("/member")
        elif typ == "int":
            res = int(lex.expect(TEXT))
            lex.expect("/int")
        elif typ == "string":
            res = lex.expect(TEXT)
            lex.expect("/string")
        elif typ == "boolean":
            res = lex.expect(TEXT) == "1"
            lex.expect("/boolean")
        else:
            raise NotImplementedError(typ)
        lex.expect("/value")
        return res


class ServerProxy:

    def __init__(self, uri, verbose=False, allow_none=False):
        self.uri = uri
        self.verbose = verbose

    def __getattr__(self, attr):
        return Method(self, attr)
