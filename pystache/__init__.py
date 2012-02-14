from pystache.template import Template
from pystache.view import View
from pystache.loader import Loader

def render(template, context=None, path=None, **kwargs):
    context = context and context.copy() or {}
    context.update(kwargs)
    view = View(context=context, path=path)
    return Template(template, view).render()
