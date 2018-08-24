import sys
# Remove current dir from sys.path, otherwise setuptools will peek up our
# module instead of system's.
sys.path.pop(0)
from setuptools import setup
sys.path.append("..")

setup(name='micropython-cpython-micropython',
      version='0.1',
      description='MicroPython module micropython ported to CPython',
      long_description='This is MicroPython compatibility module, allowing applications using\nMicroPython-specific features to run on CPython.\n',
      url='https://github.com/pfalcon/micropython-lib',
      author='Paul Sokolovsky',
      author_email='micropython-lib@googlegroups.com',
      maintainer='Paul Sokolovsky',
      maintainer_email='micropython-lib@googlegroups.com',
      license='Python',
      py_modules=['micropython'])
