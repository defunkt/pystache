import re
import cgi

SECTION_RE = re.compile(r"{{\#([^\}]*)}}\s*(.+?)\s*{{/\1}}", re.M | re.S)
TAG_RE = re.compile(r"{{(#|=|!|<|>|\{)?(.+?)\1?}}+")

class Template(object):
    tag_types = {
        None: 'tag',
        '!': 'comment',
        '{': 'unescaped',
        '>': 'partial'
    }

    def __init__(self, template, context=None):
        self.template = template
        self.context = context or {}

    def render(self, template=None, context=None):
        """Turns a Mustache template into something wonderful."""
        template = template or self.template
        context = context or self.context

        template = self.render_sections(template, context)
        return self.render_tags(template, context)

    def render_sections(self, template, context):
        """Expands sections."""
        while 1:
            match = SECTION_RE.search(template)
            if match is None:
                break

            section, section_name, inner = match.group(0, 1, 2)

            it = context.get(section_name, None)
            replacer = ''
            if it and not hasattr(it, '__iter__'):
                replacer = inner
            elif it:
                insides = []
                for item in it:
                    insides.append(self.render(inner, item))
                replacer = ''.join(insides)

            template = template.replace(section, replacer)

        return template

    def render_tags(self, template, context):
        """Renders all the tags in a template for a context."""
        while 1:
            match = TAG_RE.search(template)
            if match is None:
                break

            tag, tag_type, tag_name = match.group(0, 1, 2)
            func = 'render_' + self.tag_types[tag_type]

            if hasattr(self, func):
                replacement = getattr(self, func)(tag_name, context)
                template = template.replace(tag, replacement)

        return template

    def render_tag(self, tag_name, context):
        """Given a tag name and context, finds, escapes, and renders the tag."""
        return cgi.escape(context.get(tag_name, ''))

    def render_comment(self, tag_name=None, context=None):
        """Rendering a comment always returns nothing."""
        return ''

    def render_unescaped(self, tag_name=None, context=None):
        """Render a tag without escaping it."""
        return context.get(tag_name, '')

    def render_partial(self, tag_name=None, context=None):
        """Renders a partial within the current context."""
        # Import view here to avoid import loop
        from pystache.view import View

        view = View(context=context)
        view.template_name = tag_name

        return view.render()
