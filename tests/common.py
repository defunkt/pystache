# coding: utf-8

"""
Provides test-related code that can be used by all tests.

"""

import os


DATA_DIR = 'tests/data'

def get_data_path(file_name):
    return os.path.join(DATA_DIR, file_name)


def assert_strings(test_case, actual, expected):
    # Show both friendly and literal versions.
    message = """\


    Expected: \"""%s\"""
    Actual:   \"""%s\"""

    Expected: %s
    Actual:   %s""" % (expected, actual, repr(expected), repr(actual))
    test_case.assertEquals(actual, expected, message)


class AssertIsMixin:

    """A mixin for adding assertIs() to a unittest.TestCase."""

    # unittest.assertIs() is not available until Python 2.7:
    #   http://docs.python.org/library/unittest.html#unittest.TestCase.assertIsNone
    def assertIs(self, first, second):
        self.assertTrue(first is second, msg="%s is not %s" % (repr(first), repr(second)))
