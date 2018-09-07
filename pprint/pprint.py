def pformat(obj, indent=1, width=80, depth=None):
    return repr(obj)

def pprint(obj, stream=None, indent=1, width=80, depth=None):
    print(repr(obj), file=stream)
