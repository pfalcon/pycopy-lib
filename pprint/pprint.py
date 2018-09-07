def pformat(obj):
    return repr(obj)

def pprint(obj, stream=None):
    print(repr(obj), file=stream)
