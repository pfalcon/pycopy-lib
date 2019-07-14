# (c) 2019 Paul Sokolovsky, MIT license
from token import *
from ucollections import namedtuple


COMMENT = N_TOKENS + 0
NL = N_TOKENS + 1
ENCODING = N_TOKENS + 2
tok_name[COMMENT] = "COMMENT"
tok_name[NL] = "NL"
tok_name[ENCODING] = "ENCODING"


class TokenInfo(namedtuple("TokenInfo", ("type", "string", "start", "end", "line"))):

    def __str__(self):
        return "TokenInfo(type=%d (%s), string=%r, startl=%d, line=%r)" % (
            self.type, tok_name[self.type], self.string, self.start, self.line
        )


def get_indent(l):
    for i in range(len(l)):
        if l[i] != " ":
            return i, l[i:]


def tokenize(readline):

    indent_stack = [0]
    lineno = 0

    yield TokenInfo(ENCODING, "utf-8", 0, 0, "")

    while True:
        l = readline()
        lineno += 1
        org_l = l
        if not l:
            break
        i, l = get_indent(l)

        if l == "\n":
            yield TokenInfo(NL, l, lineno, 0, org_l)
            continue

        if l.startswith("#"):
            yield TokenInfo(COMMENT, l.rstrip("\n"), lineno, 0, org_l)
            yield TokenInfo(NL, "\n", lineno, 0, org_l)
            continue

        if i > indent_stack[-1]:
            yield TokenInfo(INDENT, " " * i, lineno, 0, org_l)
            indent_stack.append(i)
        elif i < indent_stack[-1]:
            while i != indent_stack[-1]:
                yield TokenInfo(DEDENT, "", lineno, 0, org_l)
                indent_stack.pop()

        while l:
            if l[0].isdigit():
                t = ""
                while l and (l[0].isdigit() or l[0] == "."):
                    t += l[0]
                    l = l[1:]
                yield TokenInfo(NUMBER, t, lineno, 0, org_l)
            elif l[0].isalpha() or l.startswith("_"):
                name = ""
                while l and (l[0].isalpha() or l[0].isdigit() or l.startswith("_")):
                    name += l[0]
                    l = l[1:]
                yield TokenInfo(NAME, name, lineno, 0, org_l)
            elif l[0] == "\n":
                yield TokenInfo(NEWLINE, "\n", lineno, 0, org_l)
                break
            elif l[0].isspace():
                l = l[1:]
            elif l.startswith('"') or l.startswith("'"):
                s = sep = l[0]
                l = l[1:]
                quoted = False
                while True:
                    c = l[0]
                    l = l[1:]
                    s += c
                    if quoted:
                        quoted = False
                    elif c == "\\":
                        quoted = True
                    elif c == sep:
                        break
                yield TokenInfo(STRING, s, lineno, 0, org_l)
            else:
                for op in (
                    "**=", "//=", ">>=", "<<=", "+=", "-=", "*=", "/=",
                    "%=", "@=", "&=", "|=", "^=", "**", "//", "<<", ">>",
                    "==", "!=", ">=", "<="
                ):
                    if l.startswith(op):
                        yield TokenInfo(OP, op, lineno, 0, org_l)
                        l = l[len(op):]
                        break
                else:
                    yield TokenInfo(OP, l[0], lineno, 0, org_l)
                    l = l[1:]

    while indent_stack[-1] > 0:
        yield TokenInfo(DEDENT, "", lineno, 0, "")
        indent_stack.pop()

    yield TokenInfo(ENDMARKER, "", lineno, 0, "")
