import re
import cgi
import collections
import os
import copy


class Modifiers(dict):
    """Dictionary with a decorator for assigning functions to keys."""

    def set(self, key):
        """
        Decorator function to set the given key to the decorated function.

            >>> modifiers = {}
            >>> @modifiers.set('P')
            ... def render_tongue(self, tag_name=None, context=None):
            ...     return ":P %s" % tag_name
            >>> modifiers
            {'P': <function render_tongue at 0x...>}
        """

        def setter(func):
            self[key] = func
            return func
        return setter


class Template(object):

    tag_re = None

    otag = '{{'

    ctag = '}}'

    modifiers = Modifiers()

    def __init__(self, template=None, context=None, **kwargs):
        from view import View

        self.template = template

        if kwargs:
            context.update(kwargs)

        self.view = context if isinstance(context, View) else View(context=context)
        self._compile_regexps()

    def _compile_regexps(self):
        tags = {
            'otag': re.escape(self.otag),
            'ctag': re.escape(self.ctag)
        }

        section = r"%(otag)s[\#|^]([^\}]*)%(ctag)s\s*(.+?\s*)%(otag)s/\1%(ctag)s"
        self.section_re = re.compile(section % tags, re.M|re.S)

        tag = r"%(otag)s(#|=|&|!|>|\{)?(.+?)\1?%(ctag)s+"
        self.tag_re = re.compile(tag % tags)

    def _render_sections(self, template, view):
        while True:
            match = self.section_re.search(template)
            if match is None:
                break

            section, section_name, inner = match.group(0, 1, 2)
            section_name = section_name.strip()
            it = self.view.get(section_name, None)
            replacer = ''

            # Callable
            if it and isinstance(it, collections.Callable):
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

            template = template.replace(section, replacer)

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
        self.view.context_list.insert(0, context)
        template = Template(template, self.view)
        out = template.render()
        self.view.context_list.pop(0)
        return out

    def _render_list(self, template, listing):
        insides = []
        for item in listing:
            insides.append(self._render_dictionary(template, item))

        return ''.join(insides)

    @modifiers.set(None)
    def _render_tag(self, tag_name):
        raw = self.view.get(tag_name, '')

        # For methods with no return value
        if not raw and raw is not 0:
            if tag_name == '.':
                raw = self.view.context_list[0]
            else:
                return ''

        return cgi.escape(unicode(raw))

    @modifiers.set('!')
    def _render_comment(self, tag_name):
        return ''

    @modifiers.set('>')
    def _render_partial(self, template_name):
        from pystache import Loader
        markup = Loader().load_template(template_name, self.view.template_path, encoding=self.view.template_encoding)
        template = Template(markup, self.view)
        return template.render()

    @modifiers.set('=')
    def _change_delimiter(self, tag_name):
        """Changes the Mustache delimiter."""
        self.otag, self.ctag = tag_name.split(' ')
        self._compile_regexps()
        return ''

    @modifiers.set('{')
    @modifiers.set('&')
    def render_unescaped(self, tag_name):
        """Render a tag without escaping it."""
        return unicode(self.view.get(tag_name, ''))

    def render(self, encoding=None):
        template = self._render_sections(self.template, self.view)
        result = self._render_tags(template)

        if encoding is not None:
            result = result.encode(encoding)

        return result
