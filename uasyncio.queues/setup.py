import sys
# Remove current dir from sys.path, otherwise setuptools will peek up our
# module instead of system's.
sys.path.pop(0)
from setuptools import setup
sys.path.append("..")
import sdist_upip

setup(name='micropython-uasyncio.queues',
      version='0.1.2',
      description='uasyncio.queues module for MicroPython',
      long_description='Port of asyncio.queues to uasyncio.',
      url='https://github.com/pfalcon/micropython-lib',
      author='Paul Sokolovsky',
      author_email='micropython-lib@googlegroups.com',
      maintainer='Paul Sokolovsky',
      maintainer_email='micropython-lib@googlegroups.com',
      license='MIT',
      cmdclass={'sdist': sdist_upip.sdist},
      packages=['uasyncio'],
      install_requires=['micropython-uasyncio.core', 'micropython-collections.deque'])
