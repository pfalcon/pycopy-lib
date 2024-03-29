# (c) 2014-2020 Paul Sokolovsky. MIT license.
import sys
import ffilib
import uerrno


PTR_SZ = 8 if ffilib.bitness > 32 else 4

sq3 = ffilib.open("libsqlite3")

sqlite3_open = sq3.func("i", "sqlite3_open", "sp")
#int sqlite3_close(sqlite3*);
sqlite3_close = sq3.func("i", "sqlite3_close", "p")
#int sqlite3_prepare(
#  sqlite3 *db,            /* Database handle */
#  const char *zSql,       /* SQL statement, UTF-8 encoded */
#  int nByte,              /* Maximum length of zSql in bytes. */
#  sqlite3_stmt **ppStmt,  /* OUT: Statement handle */
#  const char **pzTail     /* OUT: Pointer to unused portion of zSql */
#);
sqlite3_prepare = sq3.func("i", "sqlite3_prepare", "psipp")
#int sqlite3_finalize(sqlite3_stmt *pStmt);
sqlite3_finalize = sq3.func("i", "sqlite3_finalize", "p")
#int sqlite3_step(sqlite3_stmt*);
sqlite3_step = sq3.func("i", "sqlite3_step", "p")
#int sqlite3_column_count(sqlite3_stmt *pStmt);
sqlite3_column_count = sq3.func("i", "sqlite3_column_count", "p")
#int sqlite3_column_type(sqlite3_stmt*, int iCol);
sqlite3_column_type = sq3.func("i", "sqlite3_column_type", "pi")
#const char *sqlite3_column_name(sqlite3_stmt*, int N)
sqlite3_column_name = sq3.func("s", "sqlite3_column_name", "pi")
sqlite3_column_int64 = sq3.func("q", "sqlite3_column_int64", "pi")
# using "d" return type gives wrong results
sqlite3_column_double = sq3.func("d", "sqlite3_column_double", "pi")
sqlite3_column_text = sq3.func("s", "sqlite3_column_text", "pi")
#sqlite3_int64 sqlite3_last_insert_rowid(sqlite3*);
# TODO: should return long int
sqlite3_last_insert_rowid = sq3.func("i", "sqlite3_last_insert_rowid", "p")
#const char *sqlite3_errmsg(sqlite3*);
sqlite3_errmsg = sq3.func("s", "sqlite3_errmsg", "p")

# Too recent
##const char *sqlite3_errstr(int);
#sqlite3_errstr = sq3.func("s", "sqlite3_errstr", "i")


SQLITE_OK         = 0
SQLITE_ERROR      = 1
SQLITE_BUSY       = 5
SQLITE_MISUSE     = 21
SQLITE_ROW        = 100
SQLITE_DONE       = 101

SQLITE_INTEGER  = 1
SQLITE_FLOAT    = 2
SQLITE_TEXT     = 3
SQLITE_BLOB     = 4
SQLITE_NULL     = 5


class Error(Exception):
    pass


def check_error(db, s):
    if s != SQLITE_OK:
        raise Error(s, sqlite3_errmsg(db))


# Used as a sentinel value so far.
class Row:
    pass


class Connection:

    def __init__(self, h):
        self.h = h
        self.row_factory = None

    def cursor(self):
        return Cursor(self.h, self.row_factory)

    def close(self):
        s = sqlite3_close(self.h)
        check_error(self.h, s)


class Cursor:

    def __init__(self, h, row_factory):
        self.h = h
        self.row_factory = row_factory
        self.stmnt = None

    def execute(self, sql, params=None):
        if params:
            sql = sql.replace("?", "%s")
            params = [quote(v) for v in params]
            sql = sql % tuple(params)
        #print(sql)
        b = bytearray(PTR_SZ)
        s = sqlite3_prepare(self.h, sql, -1, b, None)
        check_error(self.h, s)
        self.stmnt = int.from_bytes(b, sys.byteorder)
        #print("stmnt", self.stmnt)
        self.num_cols = sqlite3_column_count(self.stmnt)
        #print("num_cols", self.num_cols)
        # If it's not select, actually execute it here
        # num_cols == 0 for statements which don't return data (=> modify it)
        if not self.num_cols:
            v = self.fetchone()
            assert v is None
            self.lastrowid = sqlite3_last_insert_rowid(self.h)
        return self

    def close(self):
        if self.stmnt is not None:
            s = sqlite3_finalize(self.stmnt)
            self.stmnt = None
            check_error(self.h, s)

    def make_row(self):
        is_dict = self.row_factory is Row
        if is_dict:
            res = {}
        else:
            res = []
        for i in range(self.num_cols):
            t = sqlite3_column_type(self.stmnt, i)
            #print("type", t)
            if t == SQLITE_INTEGER:
                v = sqlite3_column_int64(self.stmnt, i)
            elif t == SQLITE_FLOAT:
                v = sqlite3_column_double(self.stmnt, i)
            elif t == SQLITE_TEXT:
                v = sqlite3_column_text(self.stmnt, i)
            elif t == SQLITE_NULL:
                v = None
            else:
                raise NotImplementedError(t)
            if is_dict:
                res[sqlite3_column_name(self.stmnt, i)] = v
            else:
                res.append(v)
        if is_dict:
            return res
        else:
            return tuple(res)

    def fetchone(self):
        res = sqlite3_step(self.stmnt)
        #print("step:", res)
        if res == SQLITE_DONE:
            return None
        if res == SQLITE_ROW:
            return self.make_row()
        check_error(self.h, res)

    def __iter__(self):
        return self

    def __next__(self):
        res = self.fetchone()
        if res is None:
            raise StopIteration
        return res


def connect(fname):
    b = bytearray(PTR_SZ)
    res = sqlite3_open(fname, b)
    h = int.from_bytes(b, sys.byteorder)
    if not h:
        raise OSError(uerrno.ENOMEM)
    check_error(h, res)
    #print(h)
    return Connection(h)


def quote(val):
    if isinstance(val, str):
        val = val.replace("'", "''")
        return "'%s'" % val
    val = str(val)
    return val.replace("'", "''")
