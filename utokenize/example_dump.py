import sys
import utokenize as tokenize


f = open(sys.argv[1], "r")
for t in tokenize.generate_tokens(f.readline):
    print(t)
