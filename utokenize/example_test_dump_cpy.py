# Same as example_dump.py, but for CPython's tokenize module
import sys
import tokenize as tokenize


f = open(sys.argv[1], "rb")
for t in tokenize.tokenize(f.readline):
    #print(t)
    print("TokenInfo(type=%d (%s), string=%r, startl=%d)" % \
        (t.type, tokenize.tok_name[t.type], t.string, t.start[0]))
