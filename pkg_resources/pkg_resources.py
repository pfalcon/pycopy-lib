import uio

_c = {}

def resource_stream(package, resource):
    if package not in _c:
        try:
            if package:
                p = __import__(package + ".R", None, None, True)
            else:
                p = __import__("R")
            _c[package] = p.R
        except ImportError:
            if package:
                p = __import__(package)
                d = p.__path__
            else:
                d = "."
#            if d[0] != "/":
#                import uos
#                d = uos.getcwd() + "/" + d
            _c[package] = d + "/"

    p = _c[package]
    if isinstance(p, dict):
        return uio.BytesIO(p[resource])
    return open(p + resource, "rb")
