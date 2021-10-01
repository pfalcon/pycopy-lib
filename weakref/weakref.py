#
# This is completely dummy implementation, which does not
# provide real weak references, and thus will hoard memory!
#

WeakKeyDictionary = dict


def proxy(obj, cb=None):
    return obj
