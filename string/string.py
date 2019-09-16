# Some strings for ctype-style character classification
whitespace = ' \t\n\r\v\f'
ascii_lowercase = 'abcdefghijklmnopqrstuvwxyz'
ascii_uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
ascii_letters = ascii_lowercase + ascii_uppercase
digits = '0123456789'
hexdigits = digits + 'abcdef' + 'ABCDEF'
octdigits = '01234567'
punctuation = """!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
printable = digits + ascii_letters + punctuation + whitespace


def translate(s, map):
    import io
    sb = io.StringIO()
    for c in s:
        v = ord(c)
        if v in map:
            v = map[v]
            if isinstance(v, int):
                sb.write(chr(v))
            elif v is not None:
                sb.write(v)
        else:
            sb.write(c)
    return sb.getvalue()


# str object methods not available as builtins in Pycopy

def isidentifier(s):
    if not s:
        return False
    if s[0] not in ascii_letters and s[0] != "_":
        return False
    for c in s[1:]:
        if c not in ascii_letters and c not in digits and c != "_":
            return False
    return True

def expandtabs(s, tabsize=8):
    res = ""
    col = 0
    for c in s:
        if c == "\t":
            res += " " * (tabsize - col % tabsize)
            col = 0  # simplification
            continue
        res += c
        col += 1
        if c == "\n" or c == "\r":
            col = 0
    return res


def ljust(s, w, fill=" "):
    if len(s) >= w:
        return s
    return s + fill * (w - len(s))
