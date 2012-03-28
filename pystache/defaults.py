# coding: utf-8

"""
This module provides a central location for defining default behavior.

"""

# How to handle encoding errors when decoding strings from str to unicode.
#
# This value is passed as the "errors" argument to Python's built-in
# unicode() function:
#
#   http://docs.python.org/library/functions.html#unicode
#
DECODE_ERRORS = 'strict'

# The default template extension.
TEMPLATE_EXTENSION = 'mustache'
