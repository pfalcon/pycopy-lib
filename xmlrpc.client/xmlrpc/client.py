import uio
from urllib.urequest import urlopen
import xmltok2


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
            xmltok2.gfind(tokenizer, lambda ev: ev[0] == xmltok2.START_TAG and ev[2] == "value")
            ev = next(tokenizer)
            assert ev[0] == xmltok2.START_TAG
            typ = ev[2]
            ev = next(tokenizer)
            assert ev[0] == xmltok2.TEXT
            val = ev[1]
            if typ == "boolean":
                assert val in ("0", "1")
                return val == "1"
            else:
                assert NotImplementedError
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


class ServerProxy:

    def __init__(self, uri, verbose=False, allow_none=False):
        self.uri = uri
        self.verbose = verbose

    def __getattr__(self, attr):
        return Method(self, attr)
