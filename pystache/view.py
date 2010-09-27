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
    
    # Character encoding of the template file. If None, Pystache will not
    # do any decoding of the template.
    template_encoding = None

    def __init__(self, template=None, context=None, **kwargs):
        self.template_content = dict()
        
        if template is not None:
            self.template_content[self.get_template_name()] = template
        elif self.template is not None:
            self.template_content[self.get_template_name()] = self.template

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

    def create_template(self, template_name=None, context=None):
        content = self.load_template_content(template_name or self.get_template_name())
        context = context or self
        
        template = Template(content, context=context, template_loader=self.create_template)
        return template

    def load_template_content(self, template_name):
        # We may have content for this loaded already
        template_content = self.template_content.get(template_name)
        
        if template_content is None:
            template_content = self._load_template_content(template_name)
            self.template_content[template_name] = template_content
        return template_content

    def _load_template_content(self, template_name):
        template_file_name = '.'.join((template_name, self.template_extension))

        if isinstance(self.template_path, basestring):
            template_file_path = os.path.join(self.template_path, template_file_name)
        else:
            for path in self.template_path:
                template_file_path = os.path.join(path, template_file_name)
                if os.path.exists(template_file_path):
                    break
            else:
                raise IOError('"%s" not found in "%s"' % (template_name, ':'.join(self.template_path),))

        f = open(template_file_path, 'r')
        try:
            template = f.read()
            if self.template_encoding:
                template = unicode(template, self.template_encoding)
        finally:
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

    def __contains__(self, needle):
        return needle in self.context or hasattr(self, needle)

    def __getitem__(self, attr):
        val = self.get(attr, None)
        if not val:
            raise KeyError("No such key.")
        return val

    def get(self, attr, default):
        attr = self.context.get(attr, getattr(self, attr, default))

        if hasattr(attr, '__call__'):
            return attr()
        else:
            return attr

    def render(self, encoding=None):
        template = self.create_template()
        return template.render(encoding=encoding)

    def __str__(self):
        return self.render()
