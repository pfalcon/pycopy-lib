import builtins


def help(*sym):
    if len(sym) > 1:
        raise TypeError("function expected at most 1 arguments")

    if len(sym) == 0:
        print("""\
Welcome to MicroPython!

For online docs please visit http://pycopy.readthedocs.io/

Control commands:
  CTRL-A        -- on a blank line, enter raw REPL mode
  CTRL-B        -- on a blank line, enter normal REPL mode
  CTRL-C        -- interrupt a running program
  CTRL-D        -- on a blank line, exit or do a soft reset
  CTRL-E        -- on a blank line, enter paste mode

For further help on a specific object, type help(obj)""")
        return

    sym = sym[0]
    print("object %s is of type %s" % (sym, type(sym).__name__))
    if type(sym) is type(builtins):
        lookup_in = sym
    else:
        lookup_in = type(sym)

    for prop in dir(sym):
        if prop == "__class__":
            continue
        print("  %s -- %s" % (prop, getattr(lookup_in, prop)))


print('Type "help()" for more information.')

builtins.help = help
