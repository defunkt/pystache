from pystache.template import Template
from pystache.view import View
from pystache.loader import Loader

def render(template, context=None, path=path, **kwargs):
    context = context and context.copy() or {}
    context.update(kwargs)
    view = View(context=context)
    view.template_path = path
    return Template(template, view).render()
