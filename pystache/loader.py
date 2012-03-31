# coding: utf-8

"""
This module provides a Loader class for locating and reading templates.

"""

from __future__ import with_statement

import os
import sys

from . import defaults
from .locator import Locator


def _to_unicode(s, encoding=None):
    """
    Raises a TypeError exception if the given string is already unicode.

    """
    if encoding is None:
        encoding = defaults.STRING_ENCODING
    return unicode(s, encoding, defaults.DECODE_ERRORS)


class Loader(object):

    """
    Loads the template associated to a name or user-defined object.

    """

    def __init__(self, file_encoding=None, extension=None, to_unicode=None):
        """
        Construct a template loader instance.

        Arguments:

          extension: the template file extension.  Pass False for no
            extension (i.e. to use extensionless template files).
            Defaults to the package default.

          file_encoding: the name of the encoding to use when converting file
            contents to unicode.  Defaults to the package default.

          to_unicode: the function to use when converting strings of type
            str to unicode.  The function should have the signature:

              to_unicode(s, encoding=None)

            It should accept a string of type str and an optional encoding
            name and return a string of type unicode.  Defaults to calling
            Python's built-in function unicode() using the package encoding
            and decode-errors defaults.

        """
        if extension is None:
            extension = defaults.TEMPLATE_EXTENSION

        if file_encoding is None:
            file_encoding = defaults.FILE_ENCODING

        if to_unicode is None:
            to_unicode = _to_unicode

        self.extension = extension
        self.file_encoding = file_encoding
        self.to_unicode = to_unicode

    def unicode(self, s, encoding=None):
        """
        Convert a string to unicode using the given encoding, and return it.

        This function uses the underlying to_unicode attribute.

        Arguments:

          s: a basestring instance to convert to unicode.  Unlike Python's
            built-in unicode() function, it is okay to pass unicode strings
            to this function.  (Passing a unicode string to Python's unicode()
            with the encoding argument throws the error, "TypeError: decoding
            Unicode is not supported.")

          encoding: the encoding to pass to the to_unicode attribute.
            Defaults to None.

        """
        if isinstance(s, unicode):
            return unicode(s)

        return self.to_unicode(s, encoding)

    def read(self, path, encoding=None):
        """
        Read the template at the given path, and return it as a unicode string.

        """
        with open(path, 'r') as f:
            text = f.read()

        if encoding is None:
            encoding = self.file_encoding

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
