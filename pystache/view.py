from pystache import Template
import os.path
import re

class View(object):
    # Path where this view's template(s) live
    template_path = '.'

    # Extension for templates
    template_extension = 'mustache'

    # Absolute path to the template itself. Pystache will try to guess
    # if it's not provided.
    template_file = None

    # Contents of the template.
    template = None

    def __init__(self, template=None, context=None, **kwargs):
        self.template = template
        self.context = context or {}
        self.context.update(kwargs)

    def load_template(self):
        if self.template:
            return self.template

        if not self.template_file:
            name = self.template_name() + '.' + self.template_extension
            self.template_file = os.path.join(self.template_path, name)

        f = open(self.template_file, 'r')
        template = f.read()
        f.close()
        return template

    def template_name(self, name=None):
        """TemplatePartial => template_partial
        Takes a string but defaults to using the current class' name.
        """

        if not name:
            name = self.__class__.__name__

        def repl(match):
            return '_' + match.group(0).lower()

        return re.sub('[A-Z]', repl, name)[1:]

    def get(self, attr, default):
        if attr in self.context:
            return self.context[attr]
        elif hasattr(self, attr):
            return getattr(self, attr)()
        else:
            return default

    def render(self):
        template = self.load_template()
        return Template(template, self).render()
