# coding: utf-8

"""
This module provides a central location for defining default behavior.

Throughout the package, these defaults take effect only when the user
does not otherwise specify a value.

"""

try:
    # Python 3.2 deprecates cgi.escape() and adds the html module as a replacement.
    import html
except ImportError:
    import cgi as html

import os
import sys


# How to handle encoding errors when decoding strings from str to unicode.
#
# This value is passed as the "errors" argument to Python's built-in
# unicode() function:
#
#   http://docs.python.org/library/functions.html#unicode
#
DECODE_ERRORS = 'strict'

# The name of the encoding to use when converting to unicode any strings of
# type str encountered during the rendering process.
STRING_ENCODING = sys.getdefaultencoding()

# The name of the encoding to use when converting file contents to unicode.
# This default takes precedence over the STRING_ENCODING default for
# strings that arise from files.
FILE_ENCODING = sys.getdefaultencoding()

# The starting list of directories in which to search for templates when
# loading a template by file name.
SEARCH_DIRS = [os.curdir]  # i.e. ['.']

# The escape function to apply to strings that require escaping when
# rendering templates (e.g. for tags enclosed in double braces).
# Only unicode strings will be passed to this function.
#
# The quote=True argument causes double quotes to be escaped,
# but not single quotes:
#
#   http://docs.python.org/dev/library/html.html#html.escape
#   http://docs.python.org/library/cgi.html#cgi.escape
#
TAG_ESCAPE = lambda u: html.escape(u, quote=True)

# The default template extension.
TEMPLATE_EXTENSION = 'mustache'
