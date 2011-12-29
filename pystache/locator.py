# coding: utf-8

"""
This module provides a Locator class.

"""

import os
import re
import sys


DEFAULT_EXTENSION = 'mustache'


def make_template_name(obj):
    """
    Return the canonical template name for an object instance.

    This method converts Python-style class names (PEP 8's recommended
    CamelCase, aka CapWords) to lower_case_with_underscords.  Here
    is an example with code:

    >>> class HelloWorld(object):
    ...     pass
    >>> hi = HelloWorld()
    >>> make_template_name(hi)
    'hello_world'

    """
    template_name = obj.__class__.__name__

    def repl(match):
        return '_' + match.group(0).lower()

    return re.sub('[A-Z]', repl, template_name)[1:]


class Locator(object):

    def __init__(self, search_dirs=None, extension=None):
        """
        Construct a template locator.

        Arguments:

          search_dirs: the list of directories in which to search for templates,
            for example when looking for partials.  Defaults to the current
            working directory.  If given a string, the string is interpreted
            as a single directory.

          extension: the template file extension.  Defaults to "mustache".
            Pass False for no extension (i.e. extensionless template files).

        """
        if extension is None:
            extension = DEFAULT_EXTENSION

        if search_dirs is None:
            search_dirs = os.curdir  # i.e. "."

        if isinstance(search_dirs, basestring):
            search_dirs = [search_dirs]

        self.search_dirs = search_dirs
        self.template_extension = extension

    def make_file_name(self, template_name):
        file_name = template_name
        if self.template_extension is not False:
            file_name += os.path.extsep + self.template_extension

        return file_name

    def locate_path(self, template_name):
        """
        Find and return the path to the template with the given name.

        Raises an IOError if the template cannot be found.

        """
        search_dirs = self.search_dirs

        file_name = self.make_file_name(template_name)

        for dir_path in search_dirs:
            file_path = os.path.join(dir_path, file_name)
            if os.path.exists(file_path):
                return file_path

        # TODO: we should probably raise an exception of our own type.
        raise IOError('"%s" not found in "%s"' % (template_name, ':'.join(search_dirs),))

