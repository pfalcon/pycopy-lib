ast/types.py: ast/types.py.pre Python.asdl
	cat ast/types.py.pre >$@
	python3 asdl2py.py Python.asdl >>$@

install:
	pip3 install --user asdl
