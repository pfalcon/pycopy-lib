import io
import ujson


assert ujson.loads(b'"123"') == "123"

buf = io.BytesIO(b'"123"')
assert ujson.load(buf) == "123"

buf = io.StringIO('"123"')
assert ujson.load(buf) == "123"

assert ujson.load(open("test.json")) == "123"

assert ujson.load(open("test.json", "rb")) == "123"
