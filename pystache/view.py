from pystache import Template
import os.path
import re
from types import *

class View(object):
    
    template_name = None
    template_path = None
    template = None
    
    def __init__(self, template=None, context=None, **kwargs):
        self.template = template
        self.context = context or {}
        self.context.update(**kwargs)
        
    def get(self, attr, default=None):
        attr = self.context.get(attr, getattr(self, attr, self._get_from_parent(attr, default)))
        
        if hasattr(attr, '__call__') and type(attr) is UnboundMethodType:
            return attr()
        else:
            return attr
    
    def _get_from_parent(self, attr, default=None):
        if hasattr(self, 'parent'):
            return self.parent.get(attr, default)
        else:
            return default
    
    def get_template(self, template_name):
        if not self.template:
            from pystache import Loader
            template_name = self._get_template_name(template_name)
            self.template = Loader().load_template(template_name, self.template_path)
        
        return self.template

    def _get_template_name(self, template_name=None):
        """TemplatePartial => template_partial
        Takes a string but defaults to using the current class' name or
        the `template_name` attribute
        """
        if self.template_name:
            return self.template_name

        if not template_name:
            template_name = self.__class__.__name__

        def repl(match):
            return '_' + match.group(0).lower()

        return re.sub('[A-Z]', repl, template_name)[1:]

    def render(self):        
        return Template(self.get_template(self.template_name), self).render()