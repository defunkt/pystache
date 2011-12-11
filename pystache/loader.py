# coding: utf-8

"""
This module provides a Loader class.

"""

import os


class Loader(object):

    def __init__(self, search_dirs=None, encoding=None, extension=None):
        """
        Construct a template loader.

        Arguments:

          search_dirs: the directories in which to search for templates.
            Defaults to the current working directory.

        """
        if extension is None:
            extension = 'mustache'
        if search_dirs is None:
            search_dirs = os.curdir  # i.e. "."

        if isinstance(search_dirs, basestring):
            search_dirs = [search_dirs]

        self.search_dirs = search_dirs
        self.template_encoding = encoding
        self.template_extension = extension

    def load_template(self, template_name):
        """
        Find and load the given template, and return it as a string.

        Raises an IOError if the template cannot be found.

        """
        search_dirs = self.search_dirs
        file_name = template_name + '.' + self.template_extension

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
            if self.template_encoding:
                template = unicode(template, self.template_encoding)
        finally:
            f.close()

        return template
