# coding: utf-8

"""
This module provides a Loader class.

"""

import os
import sys

DEFAULT_EXTENSION = 'mustache'


class Loader(object):

    def __init__(self, search_dirs=None, encoding=None, extension=None):
        """
        Construct a template loader.

        Arguments:

          encoding: the name of the encoding to use when converting file
            contents to unicode.  This name will be passed as the encoding
            argument to the built-in function unicode().  Defaults to the
            encoding name returned by sys.getdefaultencoding().

          search_dirs: the directories in which to search for templates.
            Defaults to the current working directory.

          extension: the template file extension.  Defaults to "mustache".
            Pass False for no extension.

        """
        if encoding is None:
            encoding = sys.getdefaultencoding()
        if extension is None:
            extension = DEFAULT_EXTENSION
        if search_dirs is None:
            search_dirs = os.curdir  # i.e. "."

        if isinstance(search_dirs, basestring):
            search_dirs = [search_dirs]

        self.search_dirs = search_dirs
        self.template_encoding = encoding
        self.template_extension = extension

    def make_file_name(self, template_name):
        file_name = template_name
        if self.template_extension is not False:
            file_name += os.path.extsep + self.template_extension

        return file_name

    def load_template(self, template_name):
        """
        Find and load the given template, and return it as a string.

        Raises an IOError if the template cannot be found.

        """
        search_dirs = self.search_dirs

        file_name = self.make_file_name(template_name)

        for dir_path in search_dirs:
            file_path = os.path.join(dir_path, file_name)
            if os.path.exists(file_path):
                return self._load_template_file(file_path)

        # TODO: we should probably raise an exception of our own type.
        raise IOError('"%s" not found in "%s"' % (template_name, ':'.join(search_dirs),))

    def _load_template_file(self, file_path):
        """
        Read a template file, and return it as a string.

        """
        f = open(file_path, 'r')

        try:
            template = f.read()
        finally:
            f.close()

        template = unicode(template, self.template_encoding)

        return template
