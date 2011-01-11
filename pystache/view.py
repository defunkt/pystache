from pystache import Template
import os.path
import re
from types import *

class View(object):
    
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