import io
import xml.etree.ElementTree as ET


DATA = '<html attr1="val1" attr2="val2"><body>foo</body><tag1><tag2>bar</tag2>tail2</tag1>tail1</html>'


root = ET.fromstring(DATA)
assert isinstance(root, ET.Element)

et = ET.parse(io.StringIO(DATA))
assert isinstance(et, ET.ElementTree)
root = et.getroot()
assert isinstance(root, ET.Element)

print(root, root.tag, root.attrib, root[0].tag)

assert root.tag == "html"
assert root.attrib == {'attr1': 'val1', 'attr2': 'val2'}
assert root.text is None
assert root.tail is None
assert len(root) == 2

t = root[0]
assert t.tag == "body"
assert t.text == "foo"
assert t.tail is None

t = root[1]
assert t.tag == "tag1"
assert t.text is None
assert t.tail == "tail1"
assert len(t) == 1

t = t[0]
assert t.tag == "tag2"
assert t.text == "bar"
assert t.tail == "tail2"
assert len(t) == 0
