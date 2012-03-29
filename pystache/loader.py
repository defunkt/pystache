# coding: utf-8

"""
This module provides a Reader class to read a template given a path.

"""

from __future__ import with_statement

import os
import sys

from . import defaults
from .locator import Locator


class Loader(object):

    def __init__(self, encoding=None, decode_errors=None, extension=None):
        """
        Construct a template reader.

        Arguments:

          decode_errors: the string to pass as the errors argument to the
            built-in function unicode() when converting str strings to
            unicode.  Defaults to the package default.

          encoding: the file encoding.  This is the name of the encoding to
            use when converting file contents to unicode.  This name is
            passed as the encoding argument to Python's built-in function
            unicode().  Defaults to the encoding name returned by
            sys.getdefaultencoding().

          extension: the template file extension.  Pass False for no
            extension (i.e. to use extensionless template files).
            Defaults to the package default.

        """
        if decode_errors is None:
            decode_errors = defaults.DECODE_ERRORS

        if encoding is None:
            encoding = sys.getdefaultencoding()

        if extension is None:
            extension = defaults.TEMPLATE_EXTENSION

        self.decode_errors = decode_errors
        self.encoding = encoding
        self.extension = extension

    # TODO: eliminate redundancy with the Renderer class's unicode code.
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

    # TODO: unit-test this method.
    def load_name(self, name, search_dirs):
        """
        Find and return the template with the given name.

        Arguments:

          name: the name of the template.

          search_dirs: the list of directories in which to search.

        """
        locator = Locator(extension=self.extension)

        path = locator.find_path_by_name(search_dirs, name)

        return self.read(path)

    # TODO: unit-test this method.
    def load_object(self, obj, search_dirs):
        """
        Find and return the template associated to the given object.

        Arguments:

          obj: an instance of a user-defined class.

          search_dirs: the list of directories in which to search.

        """
        locator = Locator(extension=self.extension)

        path = locator.find_path_by_object(search_dirs, obj)

        return self.read(path)
