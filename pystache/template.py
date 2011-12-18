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

    def __init__(self, template=None, load_template=None, output_encoding=None):
        """
        Construct a Template instance.

        Arguments:

          template: a template string as a unicode string.  Behavior is
            undefined if the string has type str.

          context: a dictionary, Context, or View instance.

          load_template: the function for loading partials.  The function should
            accept a single template_name parameter and return a template as
            a string.  Defaults to the default Loader's load_template() method.

          output_encoding: the encoding to use when rendering to a string.
            The argument should be the name of an encoding as a string, for
            example "utf-8".  See the render() method's documentation for more
            information.

        """
        if load_template is None:
            loader = Loader()
            load_template = loader.load_template

        self.load_template = load_template
        self.output_encoding = output_encoding
        self.template = template

        self._compile_regexps()

    def _initialize_context(self, context, **kwargs):
        """
        Initialize the context attribute.

        """
        if context is None:
            context = {}

        if isinstance(context, Context):
            context = context.copy()
        else:
            context = Context(context)

        if kwargs:
            context.push(kwargs)

        self.context = context


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

        template = Template(template, load_template=self.load_template)
        out = template.render(self.context)

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
        markup = self.load_template(template_name)
        template = Template(markup, load_template=self.load_template)
        return template.render(self.context)

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

    def render(self, context=None, **kwargs):
        """
        Return the template rendered using the current context.

        The return value is a unicode string, unless the output_encoding
        attribute is not None, in which case the return value has type str
        and is encoded using that encoding.

        """
        self._initialize_context(context, **kwargs)

        template = self._render_sections(self.template)
        result = self._render_tags(template)

        if self.output_encoding is not None:
            result = result.encode(self.output_encoding)

        return result
