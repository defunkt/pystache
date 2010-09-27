import re
import cgi
import collections

try:
    import collections.Callable
    def check_callable(it):
        return isinstance(it, collections.Callable)
except ImportError:
    def check_callable(it):
        return hasattr(it, '__call__')
    

modifiers = {}
def modifier(symbol):
    """Decorator for associating a function with a Mustache tag modifier.

    @modifier('P')
    def render_tongue(self, tag_name=None, context=None):
        return ":P %s" % tag_name

    {{P yo }} => :P yo
    """
    def set_modifier(func):
        modifiers[symbol] = func
        return func
    return set_modifier


def get_or_attr(obj, name, default=None):
    try:
        return obj[name]
    except KeyError:
        return default
    except:
        try:
            return getattr(obj, name)
        except AttributeError:
            return default


class Template(object):
    # The regular expression used to find a #section
    section_re = None

    # The regular expression used to find a tag.
    tag_re = None

    # Opening tag delimiter
    otag = '{{'

    # Closing tag delimiter
    ctag = '}}'

    def __init__(self, template, context=None, template_loader=None):
        self.template = template
        self.context = context or {}
        self.compile_regexps()
        self.template_loader = template_loader

    def render(self, template=None, context=None, encoding=None):
        """Turns a Mustache template into something wonderful."""
        template = template or self.template
        context = context or self.context

        template = self.render_sections(template, context, encoding)
        result = self.render_tags(template, context, encoding)
        if encoding is not None:
            result = result.encode(encoding)
        return result

    def compile_regexps(self):
        """Compiles our section and tag regular expressions."""
        tags = { 'otag': re.escape(self.otag), 'ctag': re.escape(self.ctag) }

        section = r"%(otag)s[\#|^]([^\}]*)%(ctag)s\s*(.+?)\s*%(otag)s/\1%(ctag)s"
        self.section_re = re.compile(section % tags, re.M|re.S)

        tag = r"%(otag)s(#|=|&|!|>|\{)?(.+?)\1?%(ctag)s+"
        self.tag_re = re.compile(tag % tags)

    def render_sections(self, template, context, encoding):
        """Expands sections."""
        while 1:
            match = self.section_re.search(template)
            if match is None:
                break

            section, section_name, inner = match.group(0, 1, 2)
            section_name = section_name.strip()

            it = get_or_attr(context, section_name, None)
            replacer = ''
            if it and check_callable(it):
                replacer = it(inner)
            elif it and not hasattr(it, '__iter__'):
                if section[2] != '^':
                    replacer = inner
            elif it and hasattr(it, 'keys') and hasattr(it, '__getitem__'):
                if section[2] != '^':
                    replacer = self.render(inner, it, encoding=encoding)
            elif it:
                insides = []
                for item in it:
                    insides.append(self.render(inner, item, encoding=encoding))
                replacer = ''.join(insides)
            elif not it and section[2] == '^':
                replacer = inner

            template = template.replace(section, replacer)

        return template

    def render_tags(self, template, context, encoding):
        """Renders all the tags in a template for a context."""
        while 1:
            match = self.tag_re.search(template)
            if match is None:
                break

            tag, tag_type, tag_name = match.group(0, 1, 2)
            tag_name = tag_name.strip()
            func = modifiers[tag_type]
            replacement = func(self, tag_name, context, encoding)
            template = template.replace(tag, replacement)

        return template

    @modifier(None)
    def render_tag(self, tag_name, context, encoding):
        """Given a tag name and context, finds, escapes, and renders the tag."""
        raw = get_or_attr(context, tag_name, '')
        if not raw and raw is not 0:
            return ''
        return cgi.escape(unicode(raw))

    @modifier('!')
    def render_comment(self, tag_name=None, context=None, encoding=None):
        """Rendering a comment always returns nothing."""
        return ''

    @modifier('{')
    @modifier('&')
    def render_unescaped(self, tag_name=None, context=None, encoding=None):
        """Render a tag without escaping it."""
        return unicode(get_or_attr(context, tag_name, ''))

    @modifier('>')
    def render_partial(self, tag_name=None, context=None, encoding=None):
        """Renders a partial within the current context."""
        template = self.template_loader(tag_name, context=context)
        return template.render(encoding=encoding)

    @modifier('=')
    def render_delimiter(self, tag_name=None, context=None, encoding=None):
        """Changes the Mustache delimiter."""
        self.otag, self.ctag = tag_name.split(' ')
        self.compile_regexps()
        return ''
