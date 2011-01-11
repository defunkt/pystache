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
        return self.context.get(attr, getattr(self, attr, default))