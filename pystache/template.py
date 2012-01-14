# coding: utf-8

"""
Exposes a class that represents a parsed (or compiled) template.

This module is meant only for internal use.

"""


class ParsedTemplate(object):

    def __init__(self, parse_tree):
        self._parse_tree = parse_tree

    def render(self, context):
        """
        Returns: a string of type unicode.

        The elements of parse_tree can be any of the following:

         * a unicode string
         * the return value of a call to any of the following:

            * RenderEngine._make_get_literal():
                Args: context
                Returns: unicode
            * RenderEngine._make_get_escaped():
                Args: context
                Returns: unicode
            * RenderEngine._make_get_partial()
                Args: context
                Returns: unicode
            * RenderEngine._make_get_section()
                Args: context
                Returns: unicode
            * _make_get_inverse()
                Args: context
                Returns: unicode

        """
        get_unicode = lambda val: val(context) if callable(val) else val
        parts = map(get_unicode, self._parse_tree)
        s = ''.join(parts)

        return unicode(s)

