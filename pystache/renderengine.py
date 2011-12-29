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
        >>>
        >>> @modifiers.set('P')
        ... def render_tongue(tag_name, context):
        ...     return "%s :P" % context.get(tag_name)
        >>>
        >>> modifiers['P']('text', {'text': 'hello!'})
        'hello! :P'

        """
        def decorate(func):
            self[key] = func
            return func
        return decorate


class RenderEngine(object):

    """
    Provides a render() method.

    This class is meant only for internal use.

    As a rule, the code in this class operates on unicode strings where
    possible rather than, say, strings of type str or markupsafe.Markup.
    This means that strings obtained from "external" sources like partials
    and variable tag values are immediately converted to unicode (or
    escaped and converted to unicode) before being operated on further.
    This makes maintaining, reasoning about, and testing the correctness
    of the code much simpler.  In particular, it keeps the implementation
    of this class independent of the API details of one (or possibly more)
    unicode subclasses (e.g. markupsafe.Markup).

    """
    tag_re = None
    otag = '{{'
    ctag = '}}'

    modifiers = Modifiers()

    def __init__(self, load_partial=None, literal=None, escape=None):
        """
        Arguments:

          load_partial: the function to call when loading a partial.  The
            function should accept a string template name and return a
            template string of type unicode (not a subclass).

          literal: the function used to convert unescaped variable tag
            values to unicode, e.g. the value corresponding to a tag
            "{{{name}}}".  The function should accept a string of type
            str or unicode (or a subclass) and return a string of type
            unicode (but not a proper subclass of unicode).
                This class will only pass basestring instances to this
            function.  For example, it will call str() on integer variable
            values prior to passing them to this function.

          escape: the function used to escape and convert variable tag
            values to unicode, e.g. the value corresponding to a tag
            "{{name}}".  The function should obey the same properties
            described above for the "literal" function argument.
                This function should take care to convert any str
            arguments to unicode just as the literal function should, as
            this class will not pass tag values to literal prior to passing
            them to this function.  This allows for more flexibility,
            for example using a custom escape function that handles
            incoming strings of type markupssafe.Markup differently
            from plain unicode strings.

        """
        self.escape = escape
        self.literal = literal
        self.load_partial = load_partial

    def render(self, template, context):
        """
        Return a template rendered as a string with type unicode.

        Arguments:

          template: a template string of type unicode (but not a proper
            subclass of unicode).

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

            tag_type, tag_name, template = parts[1:]

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

    def _get_string_context(self, tag_name):
        """
        Get a value from the current context as a basestring instance.

        """
        val = self.context.get(tag_name)

        # We use "==" rather than "is" to compare integers, as using "is"
        # relies on an implementation detail of CPython.  The test about
        # rendering zeroes failed while using PyPy when using "is".
        # See issue #34: https://github.com/defunkt/pystache/issues/34
        if not val and val != 0:
            if tag_name != '.':
                return ''
            val = self.context.top()

        if not isinstance(val, basestring):
            val = str(val)

        return val

    @modifiers.set(None)
    def _render_escaped(self, tag_name):
        """
        Return a variable value as an escaped unicode string.

        """
        s = self._get_string_context(tag_name)
        return self.escape(s)

    @modifiers.set('{')
    @modifiers.set('&')
    def _render_literal(self, tag_name):
        """
        Return a variable value as a unicode string (unescaped).

        """
        s = self._get_string_context(tag_name)
        return self.literal(s)

    @modifiers.set('!')
    def _render_comment(self, tag_name):
        return ''

    @modifiers.set('>')
    def _render_partial(self, template_name):
        template = self.load_partial(template_name)
        return self._render(template)

    @modifiers.set('=')
    def _change_delimiter(self, tag_name):
        """
        Change the current delimiter.

        """
        self.otag, self.ctag = tag_name.split(' ')
        self._compile_regexps()

        return ''

    def _render(self, template):
        """
        Arguments:

          template: a template string with type unicode.

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

