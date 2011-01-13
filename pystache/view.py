from pystache import Template
import os.path
import re
from types import *

class View(object):
    
    template_name = None
    template_path = None
    template = None
    template_encoding = None
    template_extension = 'mustache'
    
    def __init__(self, template=None, context=None, **kwargs):
        self.template = template
        self.context = context or {}
        self.context.update(**kwargs)
        
    def get(self, attr, default=None):
        attr = self.context.get(attr, getattr(self, attr, default))
        if hasattr(attr, '__call__') and type(attr) is UnboundMethodType:
            return attr()
        if hasattr(attr, 'render'):
            return attr.render(encoding=self.template_encoding)
        else:
            return attr
    
    def get_template(self, template_name):
        if not self.template:
            from pystache import Loader
            template_name = self._get_template_name(template_name)
            self.template = Loader().load_template(template_name, self.template_path, encoding=self.template_encoding, extension=self.template_extension)
        
        return self.template

    def _get_template_name(self, template_name=None):
        """TemplatePartial => template_partial
        Takes a string but defaults to using the current class' name or
        the `template_name` attribute
        """
        if template_name:
            return template_name

        template_name = self.__class__.__name__

        def repl(match):
            return '_' + match.group(0).lower()

        return re.sub('[A-Z]', repl, template_name)[1:]

    def render(self, encoding=None):        
        return Template(self.get_template(self.template_name), self).render(encoding=encoding)

    def __contains__(self, needle):
        return needle in self.context or hasattr(self, needle)

    def __getitem__(self, attr):
        val = self.get(attr, None)
        if not val and val is not 0:
            raise KeyError("No such key.")
        return val
            
    def __str__(self):
        return self.render()