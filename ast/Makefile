ast/types.py: ast/types.py.pre Python.asdl
	cat ast/types.py.pre >$@
	python3 _tool_asdl2py.py Python.asdl >>$@

install:
	pip3 install --user asdl

test: testsuite metacircular
	@true

testsuite:
	./runtests.sh

metacircular:
	./test_one.sh ast/parser.py
	./test_one.sh ast/types.py
	./test_one.sh ast/__init__.py
