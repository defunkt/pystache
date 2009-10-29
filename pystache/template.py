import re

SECTION_RE = re.compile(r"{{\#([^\}]*)}}\s*(.+?)\s*{{/\1}}", re.M | re.S)

class Template(object):
    tag_types = {
        None: 'tag',
        '!': 'comment'
    }

    def __init__(self, template, context={}):
        self.template = template
        self.context = context

    def render(self, template=None, context=None):
        """Turns a Mustache template into something wonderful."""
        template = template or self.template
        context = context or self.context

        template = self.render_sections(template, context)
        return self.render_tags(template, context)

    def render_sections(self, template, context):
        """Expands sections."""
        match = SECTION_RE.search(template)

        while match:
            section, section_name, inner = match.group(0, 1, 2)
            if section_name in context and context[section_name]:
                if hasattr(context[section_name], '__iter__'):
                    insides = ''
                    for item in context[section_name]:
                        ctx = context.copy()
                        ctx.update(item)
                        insides += self.render(inner, ctx)
                    template = template.replace(section, insides)
                else:
                    template = template.replace(section, inner)
            else:
                template = template.replace(section, '')
            match = SECTION_RE.search(template)

        return template

    def render_tags(self, template, context):
        """Renders all the tags in a template for a context."""
        regexp = re.compile(r"{{(#|=|!|<|>|\{)?(.+?)\1?}}+")

        match = re.search(regexp, template)
        while match:
            tag, tag_type, tag_name = match.group(0, 1, 2)
            func = 'render_' + self.tag_types[tag_type]

            if hasattr(self, func):
                replacement = getattr(self, func)(tag_name, context)
                template = template.replace(tag, replacement)

            match = re.search(regexp, template)

        return template

    def render_tag(self, tag_name, context):
        """Given a tag name and context, finds and renders the tag."""
        return context.get(tag_name, '')

    def render_comment(self, tag_name=None, context=None):
        """Rendering a comment always returns nothing."""
        return ''
