import ffilib


libc = ffilib.libc()

strlen = libc.func("L", "strlen", "P")
