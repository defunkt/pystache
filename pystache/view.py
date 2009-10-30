import pystache
import os.path

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

    def __init__(self, template=None, context={}, **kwargs):
        self.template = template
        self.context = context

        for key in kwargs:
            self.context[key] = kwargs[key]

    def load_template(self):
        if self.template:
            return self.template

        if not self.template_file:
            name = self.template_name() + '.' + self.template_extension
            self.template_file = os.path.join(self.template_path, name)

        return open(self.template_file, 'r').read()

    def template_name(self):
        return self.__class__.__name__

    def render(self):
        template = self.load_template()
        return pystache.render(template, self.context)

