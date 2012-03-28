# coding: utf-8

"""
This module provides a Reader class to read a template given a path.

"""

from __future__ import with_statement

import os
import sys

from . import defaults


class Loader(object):

    def __init__(self, encoding=None, decode_errors=None):
        """
        Construct a template reader.

        Arguments:

          encoding: the file encoding.  This is the name of the encoding to
            use when converting file contents to unicode.  This name is
            passed as the encoding argument to Python's built-in function
            unicode().  Defaults to the encoding name returned by
            sys.getdefaultencoding().

          decode_errors: the string to pass as the errors argument to the
            built-in function unicode() when converting str strings to
            unicode.  Defaults to the package default.

        """
        if decode_errors is None:
            decode_errors = defaults.DECODE_ERRORS

        if encoding is None:
            encoding = sys.getdefaultencoding()

        self.decode_errors = decode_errors
        self.encoding = encoding

    def unicode(self, s, encoding=None):
        """
        Call Python's built-in function unicode(), and return the result.

        For unicode strings (or unicode subclasses), this function calls
        Python's unicode() without the encoding and errors arguments.
        Thus, unlike Python's built-in unicode(), it is okay to pass unicode
        strings to this function.  (Passing a unicode string to Python's
        unicode() with the encoding argument throws the following
        error: "TypeError: decoding Unicode is not supported.")

        """
        if isinstance(s, unicode):
            return unicode(s)

        if encoding is None:
            encoding = self.encoding

        return unicode(s, encoding, self.decode_errors)

    def read(self, path, encoding=None):
        """
        Read the template at the given path, and return it as a unicode string.

        """
        with open(path, 'r') as f:
            text = f.read()

        return self.unicode(text, encoding)
