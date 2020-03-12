set -e

python3.5 example_ast_parse_cpy.py $1 >$1.cpy
pycopy -X heapsize=34M example_ast_parse_stream.py $1 >$1.upy
diff -u $1.cpy $1.upy
