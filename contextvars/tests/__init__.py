import os.path
import sys
import unittest


def suite():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover(
        os.path.dirname(__file__), pattern='test_*.py')
    return test_suite


if __name__ == '__main__':
    runner = unittest.TestRunner()
    result = runner.run(suite())
    sys.exit(not result.wasSuccessful())
