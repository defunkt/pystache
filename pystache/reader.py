# coding: utf-8

"""
This module provides a Reader class to read a template given a path.

"""

from __future__ import with_statement

import os
import sys


DEFAULT_DECODE_ERRORS = 'strict'


class Reader(object):

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
            built-in function unicode() when converting file contents to
            unicode.  Defaults to "strict".

        """
        if decode_errors is None:
            decode_errors = DEFAULT_DECODE_ERRORS

        if encoding is None:
            encoding = sys.getdefaultencoding()

        self.decode_errors = decode_errors
        self.encoding = encoding

    def unicode(self, text, encoding=None):
        if encoding is None:
            encoding = self.encoding

        return unicode(text, encoding, self.decode_errors)

    def read(self, path, encoding=None):
        """
        Read the template at the given path, and return it as a unicode string.

        """
        with open(path, 'r') as f:
            text = f.read()

        return self.unicode(text, encoding)
