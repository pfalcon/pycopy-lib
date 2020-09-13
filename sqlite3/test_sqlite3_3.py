import sqlite3


conn = sqlite3.connect(":memory:")

cur = conn.cursor()
cur.execute("CREATE TABLE foo(a varchar(200))")
cur.execute("INSERT INTO foo VALUES (?)", ("f'); DROP TABLE foo; SELECT ('",))
assert cur.lastrowid == 1
cur.execute("SELECT * FROM foo")
assert cur.fetchone() == ("f'); DROP TABLE foo; SELECT ('",)
assert cur.fetchone() is None
