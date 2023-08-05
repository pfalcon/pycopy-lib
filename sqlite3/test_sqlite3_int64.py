import sqlite3


conn = sqlite3.connect(":memory:")

cur = conn.cursor()
cur.execute("SELECT 10000000000")

expected = [(10000000000,)]

while True:
    row = cur.fetchone()
    if row is None:
        break
    print(row)
    e = expected.pop(0)
    assert row == e

assert expected == []
