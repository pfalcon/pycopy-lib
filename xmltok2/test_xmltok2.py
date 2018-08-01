import xmltok2

expected = [
['PI', 'xml', None, None],
['ATTR', '', 'version', '1.0'],
['START_TAG', 's', 'Envelope', None],
['ATTR', 'xmlns', 's', 'http://schemas.xmlsoap.org/soap/envelope/'],
['ATTR', 's', 'encodingStyle', 'http://schemas.xmlsoap.org/soap/encoding/'],
['START_TAG', 's', 'Body', None],
['START_TAG', 'u', 'GetConnectionTypeInfo', None],
['ATTR', 'xmlns', 'u', 'urn:schemas-upnp-org:service:WANIPConnection:1'],
['TEXT', 'foo bar\n  baz\n  \n', None, None],
['END_TAG', 'u', 'GetConnectionTypeInfo', None],
['END_TAG', 's', 'Body', None],
['START_TAG', '', 'foo', None],
['ATTR', '', 'attr', 'singlequote'],
['END_TAG', '', 'foo', None],
['START_TAG', '', 'foo2', None],
['END_TAG', '', 'foo2', None],
['END_TAG', 's', 'Envelope', None],
]

dir = "."
if "/" in __file__:
    dir = __file__.rsplit("/", 1)[0]

ex = iter(expected)
for i in xmltok2.tokenize(open(dir + "/test.xml")):
    print(i)
    assert i == next(ex)
