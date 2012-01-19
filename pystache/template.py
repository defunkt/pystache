# coding: utf-8

"""
Exposes a class that represents a parsed (or compiled) template.

This module is meant only for internal use.

"""


class ParsedTemplate(object):

    def __init__(self, parse_tree):
        """
        Arguments:

          parse_tree: a list, each element of which is either--

            (1) a unicode string, or
            (2) a "rendering" callable that accepts a Context instance
                and returns a unicode string.

        The possible rendering callables are the return values of the
        following functions:

        * RenderEngine._make_get_escaped()
        * RenderEngine._make_get_inverse()
        * RenderEngine._make_get_literal()
        * RenderEngine._make_get_partial()
        * RenderEngine._make_get_section()

        """
        self._parse_tree = parse_tree

    def render(self, context):
        """
        Returns: a string of type unicode.

        """
        get_unicode = lambda val: val(context) if callable(val) else val
        parts = map(get_unicode, self._parse_tree)
        s = ''.join(parts)

        return unicode(s)

