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


