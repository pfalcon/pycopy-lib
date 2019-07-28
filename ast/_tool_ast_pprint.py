# (c) 2019 Paul Sokolovsky. MIT license.
import sys
import ast
from ast import AST, iter_fields


def quote_uni(s):
    res = ""
    for c in s:
        v = ord(c)
        if v < 0x100:
            res += c
        elif v < 0x10000:
            res += "\\u%04x" % v
        else:
            res += "\\U%08x" % v
    return res


def dump_to_stream(node, stream):
    """
    Return a formatted dump of the tree in *node*.  This is mainly useful for
    debugging purposes.  The returned string will show the names and the values
    for fields.  This makes the code impossible to evaluate, so if evaluation is
    wanted *annotate_fields* must be set to False.  Attributes such as line
    numbers and column offsets are not dumped by default.  If this is wanted,
    *include_attributes* can be set to True.
    """
    def _format(node, indent, indent_now=True):
        if isinstance(node, AST):
            if indent_now:
                stream.write("  " * indent)
            stream.write("%s(\n" % node.__class__.__name__)

            if isinstance(node, ast.Str):
                stream.write("  " * (indent + 1))
                stream.write("s=")
                stream.write(quote_uni(node.s))
                stream.write("\n%s) # %s %d" % ("  " * indent, node.__class__.__name__, 0))
                return

            for field, val in iter_fields(node):
                stream.write("%s%s=" % ("  " * (indent + 1), field))
                if isinstance(val, list):
                    if not val:
                        stream.write("[]\n")
                    else:
                        need_comma = False
                        stream.write("[\n")
                        for n in val:
                            if need_comma:
                                stream.write("\n")
                            _format(n, indent + 2)
                            need_comma = True
                        stream.write("\n%s] # %s\n" % ("  " * (indent + 1), field))
                else:
                    _format(val, indent + 1, False)
                    stream.write("\n")

            stream.write("%s) # %s" % ("  " * indent, node.__class__.__name__))
            #"%d" % getattr(node, "lineno", -1))

        elif isinstance(node, list):
            assert 0

        else:
            if indent_now:
                stream.write("  " * indent)
            stream.write(repr(node))

    return _format(node, 0)


def dump_to_stdout(node):
    dump_to_stream(node, sys.stdout)
