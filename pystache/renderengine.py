# coding: utf-8

"""
Defines a class responsible for rendering logic.

"""

import collections
import re


try:
    # The collections.Callable class is not available until Python 2.6.
    import collections.Callable
    def check_callable(it):
        return isinstance(it, collections.Callable)
except ImportError:
    def check_callable(it):
        return hasattr(it, '__call__')


class Modifiers(dict):

    """Dictionary with a decorator for assigning functions to keys."""

    def set(self, key):
        """
        Return a decorator that assigns the given function to the given key.

        >>> modifiers = Modifiers()
        >>> @modifiers.set('P')
        ... def render_tongue(self, tag_name=None, context=None):
        ...     return ":P %s" % tag_name
        >>> modifiers
        {'P': <function render_tongue at 0x...>}

        """
        def decorate(func):
            self[key] = func
            return func
        return decorate


class RenderEngine(object):

    """
    Provides a render() method.

    This class is meant only for internal use by the Template class.

    """
    tag_re = None
    otag = '{{'
    ctag = '}}'

    modifiers = Modifiers()

    def __init__(self, load_partial=None, literal=None, escape=None):
        """
        Arguments:

          load_partial: a function for loading templates by name when
            loading partials.  The function should accept a template name
            and return a unicode template string.

          escape: a function that takes a unicode or str string,
            converts it to unicode, and escapes and returns it.

          literal: a function that converts a unicode or str string
            to unicode without escaping, and returns it.

        """
        self.escape = escape
        self.literal = literal
        self.load_partial = load_partial

    def render(self, template, context):
        """
        Arguments:

          template: a unicode template string.
          context: a Context instance.

        """
        self.context = context

        self._compile_regexps()

        return self._render(template)

    def _compile_regexps(self):
        """
        Compile and set the regular expression attributes.

        This method uses the current values for the otag and ctag attributes.

        """
        tags = {
            'otag': re.escape(self.otag),
            'ctag': re.escape(self.ctag)
        }

        # The section contents include white space to comply with the spec's
        # requirement that sections not alter surrounding whitespace.
        section = r"%(otag)s([#|^])([^\}]*)%(ctag)s(.+?)%(otag)s/\2%(ctag)s" % tags
        self.section_re = re.compile(section, re.M|re.S)

        tag = r"%(otag)s(#|=|&|!|>|\{)?(.+?)\1?%(ctag)s+" % tags
        # We use re.DOTALL to permit multiline comments, in accordance with the spec.
        self.tag_re = re.compile(tag, re.DOTALL)

    def _render_tags(self, template):
        output = []

        while True:
            parts = self.tag_re.split(template, maxsplit=1)
            output.append(parts[0])

            if len(parts) < 2:
                # Then there was no match.
                break

            start, tag_type, tag_name, template = parts

            tag_name = tag_name.strip()
            func = self.modifiers[tag_type]
            tag_value = func(self, tag_name)

            # Appending the tag value to the output prevents treating the
            # value as a template string (bug: issue #44).
            output.append(tag_value)

        output = "".join(output)
        return output

    def _render_dictionary(self, template, context):
        self.context.push(context)
        out = self._render(template)
        self.context.pop()

        return out

    def _render_list(self, template, listing):
        insides = []
        for item in listing:
            insides.append(self._render_dictionary(template, item))

        return ''.join(insides)

    @modifiers.set(None)
    def _render_tag(self, tag_name):
        """
        Return the value of a variable as an escaped unicode string.

        """
        raw = self.context.get(tag_name, '')

        # For methods with no return value
        #
        # We use "==" rather than "is" to compare integers, as using "is" relies
        # on an implementation detail of CPython.  The test about rendering
        # zeroes failed while using PyPy when using "is".
        # See issue #34: https://github.com/defunkt/pystache/issues/34
        if not raw and raw != 0:
            if tag_name == '.':
                raw = self.context.top()
            else:
                return ''

        # If we don't first convert to a string type, the call to self._unicode_and_escape()
        # will yield an error like the following:
        #
        #   TypeError: coercing to Unicode: need string or buffer, ... found
        #
        if not isinstance(raw, basestring):
            raw = str(raw)

        return self.escape(raw)

    @modifiers.set('!')
    def _render_comment(self, tag_name):
        return ''

    @modifiers.set('>')
    def _render_partial(self, template_name):
        markup = self.load_partial(template_name)
        return self._render(markup)

    @modifiers.set('=')
    def _change_delimiter(self, tag_name):
        """
        Change the current delimiter.

        """
        self.otag, self.ctag = tag_name.split(' ')
        self._compile_regexps()

        return ''

    @modifiers.set('{')
    @modifiers.set('&')
    def _render_unescaped(self, tag_name):
        """
        Render a tag without escaping it.

        """
        return self.literal(self.context.get(tag_name, ''))

    def _render(self, template):
        """
        Arguments:

          template: a unicode template string.

        """
        output = []

        while True:
            parts = self.section_re.split(template, maxsplit=1)

            start = self._render_tags(parts[0])
            output.append(start)

            if len(parts) < 2:
                # Then there was no match.
                break

            section_type, section_key, section_contents, template = parts[1:]

            section_key = section_key.strip()
            section_value = self.context.get(section_key, None)

            rendered = ''

            # Callable
            if section_value and check_callable(section_value):
                rendered = section_value(section_contents)

            # Dictionary
            elif section_value and hasattr(section_value, 'keys') and hasattr(section_value, '__getitem__'):
                if section_type != '^':
                    rendered = self._render_dictionary(section_contents, section_value)

            # Lists
            elif section_value and hasattr(section_value, '__iter__'):
                if section_type != '^':
                    rendered = self._render_list(section_contents, section_value)

            # Other objects
            elif section_value and isinstance(section_value, object):
                if section_type != '^':
                    rendered = self._render_dictionary(section_contents, section_value)

            # Falsey and Negated or Truthy and Not Negated
            elif (not section_value and section_type == '^') or (section_value and section_type != '^'):
                rendered = self._render_dictionary(section_contents, section_value)

            # Render template prior to section too
            output.append(rendered)

        output = "".join(output)
        return output

