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


# str object methods not available as builtins in MicroPython

def isidentifier(s):
    if s[0] not in ascii_letters and s[0] != "_":
        return False
    for c in s[1:]:
        if c not in ascii_letters and c not in digits and c != "_":
            return False
    return True
