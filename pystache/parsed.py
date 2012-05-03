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
            (2) a "rendering" callable that accepts a ContextStack instance
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

    def __repr__(self):
        return "[%s]" % (", ".join([repr(part) for part in self._parse_tree]))

    def render(self, context):
        """
        Returns: a string of type unicode.

        """
        # We avoid use of the ternary operator for Python 2.4 support.
        def get_unicode(val):
            if callable(val):
                return val(context)
            return val
        parts = map(get_unicode, self._parse_tree)
        s = ''.join(parts)

        return unicode(s)

