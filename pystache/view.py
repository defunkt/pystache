from pystache import Template
import os.path
import re

class View(object):
    # Path where this view's template(s) live
    template_path = '.'

    # Extension for templates
    template_extension = 'mustache'

    # The name of this template. If none is given the View will try
    # to infer it based on the class name.
    template_name = None

    # Absolute path to the template itself. Pystache will try to guess
    # if it's not provided.
    template_file = None

    # Contents of the template.
    template = None

    def __init__(self, template=None, context=None, **kwargs):
        self.template = template
        self.context = context or {}

        # If the context we're handed is a View, we want to inherit
        # its settings.
        if isinstance(context, View):
            self.inherit_settings(context)

        if kwargs:
            self.context.update(kwargs)

    def inherit_settings(self, view):
        """Given another View, copies its settings."""
        if view.template_path:
            self.template_path = view.template_path

        if view.template_name:
            self.template_name = view.template_name

    def __contains__(self, needle):
        return hasattr(self, needle)

    def __getitem__(self, attr):
        return getattr(self, attr)()

    def load_template(self):
        if self.template:
            return self.template

        if not self.template_file:
            name = self.get_template_name() + '.' + self.template_extension
            self.template_file = os.path.join(self.template_path, name)

        f = open(self.template_file, 'r')
        template = f.read()
        f.close()
        return template

    def get_template_name(self, name=None):
        """TemplatePartial => template_partial
        Takes a string but defaults to using the current class' name or
        the `template_name` attribute
        """
        if self.template_name:
            return self.template_name

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
