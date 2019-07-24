import sys
import utokenize as tokenize


f = open(sys.argv[1], "r")
for t in tokenize.tokenize(f.readline):
    print(t)
