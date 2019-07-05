ast.py: ast.py.pre Python.asdl
	cat ast.py.pre >$@
	python3 asdl2py.py Python.asdl >>$@

install:
	pip3 install --user asdl
