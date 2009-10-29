import re

class Pystache(object):
    @staticmethod
    def render(template, context):
        return Template(template, context).render()

class Template(object):
    def __init__(self, template, context={}):
        self.template = template
        self.context = context

    def render(self):
        return self.render_tags()

    def render_tags(self):
        regexp = re.compile(r"{{(#|=|!|<|>|\{)?(.+?)\1?}}+")
        template = self.template

        match = re.search(regexp, template)
        while match:
            tag, tag_name = match.group(0, 2)
            if tag_name in self.context:
                template = template.replace(tag, self.context[tag_name])
            match = re.search(regexp, template)

        return template

