import uio
from urllib.urequest import urlopen
import xmltok2


class Method:

    def __init__(self, server, name):
        self.server = server
        self.name = name

    def __call__(self, *args):
        buf = uio.StringIO()
        buf.write("<?xml version='1.0'?>\n<methodCall>\n<methodName>")
        buf.write(self.name)
        buf.write("</methodName>\n<params>\n")
        for a in args:
            buf.write("<param><value>")
            if isinstance(a, int):
                buf.write("<int>%s</int>" % a)
            else:
                raise NotImplementedError
            buf.write("</value></param>\n")
        buf.write("</params>\n</methodCall>\n")
        if self.server.verbose:
            print(buf.getvalue())
        body = buf.getvalue().encode()

        f = urlopen(self.server.uri, body, "POST")

        try:
            #print(f.read())
            f = f.makefile()
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


class ServerProxy:

    def __init__(self, uri, verbose=False):
        self.uri = uri
        self.verbose = verbose

    def __getattr__(self, attr):
        return Method(self, attr)
