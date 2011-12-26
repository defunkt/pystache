# coding: utf-8

"""
This module provides a Loader class.

"""

import os
import sys

from .reader import Reader


DEFAULT_EXTENSION = 'mustache'


class Loader(object):

    def __init__(self, search_dirs=None, extension=None, reader=None):
        """
        Construct a template loader.

        Arguments:

          search_dirs: the list of directories in which to search for templates,
            for example when looking for partials.  Defaults to the current
            working directory.  If given a string, the string is interpreted
            as a single directory.

          extension: the template file extension.  Defaults to "mustache".
            Pass False for no extension (i.e. extensionless template files).

          reader: the Reader instance to use to read file contents and
            return them as unicode strings.  Defaults to constructing
            the default Reader with no constructor arguments.

        """
        if reader is None:
            reader = Reader()

        if extension is None:
            extension = DEFAULT_EXTENSION

        if search_dirs is None:
            search_dirs = os.curdir  # i.e. "."

        if isinstance(search_dirs, basestring):
            search_dirs = [search_dirs]

        self.reader = reader
        self.search_dirs = search_dirs
        self.template_extension = extension

    def _read(self, path):
        """
        Read and return a template as a unicode string.

        """
        return self.reader.read(path)

    def make_file_name(self, template_name):
        file_name = template_name
        if self.template_extension is not False:
            file_name += os.path.extsep + self.template_extension

        return file_name

    def get(self, template_name):
        """
        Find and load the given template, and return it as a string.

        Raises an IOError if the template cannot be found.

        """
        search_dirs = self.search_dirs

        file_name = self.make_file_name(template_name)

        for dir_path in search_dirs:
            file_path = os.path.join(dir_path, file_name)
            if os.path.exists(file_path):
                return self._read(file_path)

        # TODO: we should probably raise an exception of our own type.
        raise IOError('"%s" not found in "%s"' % (template_name, ':'.join(search_dirs),))

