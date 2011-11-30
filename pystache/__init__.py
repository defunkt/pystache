from pystache.template import Template
from pystache.view import View
from pystache.loader import Loader

def render(template, context=None, **kwargs):
    context = context and context.copy() or {}
    context.update(kwargs)
    return Template(template, context).render()

