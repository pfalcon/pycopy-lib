import sys
import utokenize as tokenize


f = open(sys.argv[1], "r")
for t in tokenize.tokenize(f.readline):
    #print(t)
    print("TokenInfo(type=%d (%s), string=%r, startl=%d)" % \
        (t.type, tokenize.tok_name[t.type], t.string, t.start))
