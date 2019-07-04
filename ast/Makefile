ast.py: Python.asdl
	cat ast.py.pre >$@
	python3 asdl2py.py $^ >>$@

install:
	pip3 install --user asdl
