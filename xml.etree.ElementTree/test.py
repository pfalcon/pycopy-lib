import io
import xml.etree.ElementTree as ET


DATA = '<html attr1="val1" attr2="val2"><body>foo</body></html>'


root = ET.fromstring(DATA)
assert isinstance(root, ET.Element)

et = ET.parse(io.StringIO(DATA))
assert isinstance(et, ET.ElementTree)
root = et.getroot()
assert isinstance(root, ET.Element)

print(root, root.tag, root.attrib, root[0].tag)

assert root.tag == "html"
assert root.attrib == {'attr1': 'val1', 'attr2': 'val2'}
assert len(root) == 1
