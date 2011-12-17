# coding: utf-8

"""
This module provides a Template class.

"""

import re
import cgi
import collections

from .context import Context
from .loader import Loader


try:
    import markupsafe
    escape = markupsafe.escape
    literal = markupsafe.Markup
except ImportError:
    escape = lambda x: cgi.escape(unicode(x))
    literal = unicode


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

        >>> modifiers = {}
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


class Template(object):

    tag_re = None
    otag = '{{'
    ctag = '}}'

    modifiers = Modifiers()

    def __init__(self, template=None, context=None, **kwargs):
        """
        The context argument can be a dictionary, View, or Context instance.

        """
        from .view import View

        if context is None:
            context = {}

        view = None

        if isinstance(context, View):
            view = context
            context = view.context.copy()
        elif isinstance(context, Context):
            context = context.copy()
        else:
            # Otherwise, the context is a dictionary.
            context = Context(context)

        if kwargs:
            context.push(kwargs)

        if view is None:
            view = View()

        self.context = context
        self.template = template
        # The view attribute is used only for its load_template() method.
        self.view = view

        self._compile_regexps()

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
        section = r"%(otag)s[\#|^]([^\}]*)%(ctag)s(.+?)%(otag)s/\1%(ctag)s"
        self.section_re = re.compile(section % tags, re.M|re.S)

        tag = r"%(otag)s(#|=|&|!|>|\{)?(.+?)\1?%(ctag)s+"
        self.tag_re = re.compile(tag % tags)

    def _render_sections(self, template):
        while True:
            match = self.section_re.search(template)
            if match is None:
                break

            section, section_name, inner = match.group(0, 1, 2)
            section_name = section_name.strip()
            it = self.context.get(section_name, None)
            replacer = ''

            # Callable
            if it and check_callable(it):
                replacer = it(inner)

            # Dictionary
            elif it and hasattr(it, 'keys') and hasattr(it, '__getitem__'):
                if section[2] != '^':
                    replacer = self._render_dictionary(inner, it)

            # Lists
            elif it and hasattr(it, '__iter__'):
                if section[2] != '^':
                    replacer = self._render_list(inner, it)

            # Other objects
            elif it and isinstance(it, object):
                if section[2] != '^':
                    replacer = self._render_dictionary(inner, it)

            # Falsey and Negated or Truthy and Not Negated
            elif (not it and section[2] == '^') or (it and section[2] != '^'):
                replacer = self._render_dictionary(inner, it)

            template = literal(template.replace(section, replacer))

        return template

    def _render_tags(self, template):
        while True:
            match = self.tag_re.search(template)
            if match is None:
                break

            tag, tag_type, tag_name = match.group(0, 1, 2)
            tag_name = tag_name.strip()
            func = self.modifiers[tag_type]
            replacement = func(self, tag_name)
            template = template.replace(tag, replacement)

        return template

    def _render_dictionary(self, template, context):
        self.context.push(context)

        template = Template(template, self.context)
        template.view = self.view
        out = template.render()

        self.context.pop()

        return out

    def _render_list(self, template, listing):
        insides = []
        for item in listing:
            insides.append(self._render_dictionary(template, item))

        return ''.join(insides)

    @modifiers.set(None)
    def _render_tag(self, tag_name):
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

        return escape(raw)

    @modifiers.set('!')
    def _render_comment(self, tag_name):
        return ''

    @modifiers.set('>')
    def _render_partial(self, template_name):
        markup = self.view.load_template(template_name)
        template = Template(markup, self.context)
        template.view = self.view
        return template.render()

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
    def render_unescaped(self, tag_name):
        """
        Render a tag without escaping it.

        """
        return literal(self.context.get(tag_name, ''))

    def render(self, encoding=None):
        """
        Return the template rendered using the current view context.

        """
        template = self._render_sections(self.template)
        result = self._render_tags(template)

        if encoding is not None:
            result = result.encode(encoding)

        return result
