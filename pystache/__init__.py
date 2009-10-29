import re

class Pystache(object):
    @staticmethod
    def render(template, context={}):
        return Template(template, context).render()

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
        return self.render_tags(template, context)

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
        if tag_name in context:
            return context[tag_name]
        else:
            return ''

    def render_comment(self, tag_name=None, context=None):
        """Rendering a comment always returns nothing."""
        return ''

