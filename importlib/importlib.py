import imp

def import_module(name, package=None):
    """Import a module.

    The 'package' argument is required when performing a relative import. It
    specifies the package to use as the anchor point from which to resolve the
    relative import to an absolute import.

    """
    level = 0
    if name.startswith('.'):
        if not package:
            msg = ("the 'package' argument is required to perform a relative "
                   "import for {!r}")
            raise TypeError(msg.format(name))
        for character in name:
            if character != '.':
                break
            level += 1
        if level > 1:
            name = ".".join(package.split('.')[:1-level]) + name[level-1:]
        else:
            name = package + name

    res = imp.org_import(name)
    for n in name.split(".")[1:]:
        res = getattr(res,n)
    return res

