import uio

from uyaml import YamlParser, dump


class Dumper:
    pass


def add_representer(type, representer_func):
    pass


def safe_load(stream):
    if isinstance(stream, str):
        stream = uio.StringIO(stream)
    p = YamlParser(stream)
    return p.parse()
