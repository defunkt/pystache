# coding: utf-8

"""
Provides test-related code that can be used by all tests.

"""

import os

import examples


DATA_DIR = 'tests/data'
EXAMPLES_DIR = os.path.dirname(examples.__file__)


def get_data_path(file_name):
    return os.path.join(DATA_DIR, file_name)


class AssertStringMixin:

    """A unittest.TestCase mixin to check string equality."""

    def assertString(self, actual, expected):
        """
        Assert that the given strings are equal and have the same type.

        """
        # Show both friendly and literal versions.
        message = """String mismatch: %%s\


        Expected: \"""%s\"""
        Actual:   \"""%s\"""

        Expected: %s
        Actual:   %s""" % (expected, actual, repr(expected), repr(actual))

        self.assertEquals(actual, expected, message % "different characters")

        details = "types different: %s != %s" % (repr(type(expected)), repr(type(actual)))
        self.assertEquals(type(expected), type(actual), message % details)


class AssertIsMixin:

    """A unittest.TestCase mixin adding assertIs()."""

    # unittest.assertIs() is not available until Python 2.7:
    #   http://docs.python.org/library/unittest.html#unittest.TestCase.assertIsNone
    def assertIs(self, first, second):
        self.assertTrue(first is second, msg="%s is not %s" % (repr(first), repr(second)))


class Attachable(object):
    """A trivial object that attaches all constructor named parameters as attributes.
    For instance,

    >>> o = Attachable(foo=42, size="of the universe")
    >>> o.foo
    42
    >>> o.size
    of the universe
    """
    def __init__(self, **kwargs):
        self.__args__ = kwargs
        for arg, value in kwargs.iteritems():
            setattr(self, arg, value)

    def __repr__(self):
        return "A(%s)" % (", ".join("%s=%s" % (k, v)
                                    for k, v in self.__args__.iteritems()))
